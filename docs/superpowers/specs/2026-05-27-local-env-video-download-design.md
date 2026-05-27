# Local Environment & Universal Video Download — Design Spec

**Date:** 2026-05-27
**Branch target:** feature/local-env-video-download (TBD by implementer)
**Sub-project:** A (of A → B → C decomposition; B = dataset completion, C = design/UX upgrade)
**Status:** Draft for implementation

## Goal

Make the local development environment "just work": one command brings the stack up, any public video URL from the must-have platform set downloads reliably, and progress/errors are surfaced clearly in the UI.

## Non-Goals

- Detection-quality improvements (belongs to B).
- Frontend visual redesign or new UX surfaces beyond progress/error text (belongs to C).
- External download microservice or proxy rotation.
- Production deployment changes.

## Success Criteria (Definition of Done)

1. `scripts/local-up.ps1` (Windows) or `scripts/local-up.sh` (POSIX) starts the full stack and prints `READY` within 120 seconds on a clean machine with Docker installed.
2. `GET /api/v1/health/ready` returns 200 with per-check status; 503 if any critical check fails. `GET /api/v1/health/live` always returns 200 when the process is up.
3. Smoke download succeeds for at least one public URL from each must-have platform: YouTube (long + Shorts), TikTok, Instagram Reels, VK, Telegram, Rutube, Twitter/X.
4. On download failure the user sees a stable `user_message` plus a `hint_action` (`provide_cookies` | `install_ffmpeg` | `retry_later` | `unsupported_url` | `unknown`).
5. `VideoProcessor.process(url=...)` public contract is unchanged. All existing unit/integration tests still pass.

## Must-Have Platforms

YouTube (long + Shorts), TikTok, Instagram Reels, VK, Telegram, Rutube, Twitter/X. Other platforms covered through generic `yt-dlp` handler (best-effort).

## Architecture

Three layers, no new external services.

### 1. Bootstrap Layer

- `scripts/local-up.ps1` and `scripts/local-up.sh`: one entry point. Steps:
  1. If `.env` missing, copy from `.env.example`. Same for `backend/.env` and `frontend/.env.local`.
  2. `docker compose -f docker-compose.local.yml up -d`.
  3. Poll `GET http://localhost:8000/api/v1/health/ready` every 3 seconds, timeout 120 seconds.
  4. Print URLs (`http://localhost:3000`, `http://localhost:8000/docs`) and a per-check status table.
- `scripts/local-down.{ps1,sh}`: `docker compose down`.
- `Makefile` targets `local`, `local-down` wrapping the scripts on POSIX (Windows users invoke `.ps1` directly).

### 2. Preflight / Health Layer

Location: `backend/app/core/preflight.py` (new module).

`async run_checks() -> dict[name, CheckResult]` runs all checks concurrently with 5-second per-check timeout:

| Check | Method | Failure semantics |
|---|---|---|
| `ffmpeg` | `shutil.which("ffmpeg")` and `shutil.which("ffprobe")` | critical |
| `yt_dlp` | `import yt_dlp; yt_dlp.version.__version__` | critical |
| `cookies` | `Path(settings.YTDLP_COOKIES_FILE).exists()` plus size > 0; report age in days | warning (not critical) |
| `redis` | `redis.ping()` | critical |
| `db` | `SELECT 1` against configured database | critical |
| `data_dirs` | `models/`, `data/uploads/`, `data/processed/` exist and are writable | critical |
| `models_warm` | `model_manager.is_warm` | warning |

`CheckResult = { name: str, status: "ok"|"warning"|"failed", message: str, duration_ms: int }`.
Cached for 30 seconds.

Endpoints (added to existing FastAPI router):

- `GET /api/v1/health/live` — `{ok: true}`, no checks. For container liveness probe.
- `GET /api/v1/health/ready` — `{ready: bool, checks: [CheckResult...], models_warm: bool, warnings: [str...]}`. Returns 200 if no critical check failed, else 503.

### 3. Download Layer

Refactor: extract download logic from `backend/app/services/video_processor.py` into `backend/app/services/downloaders/`.

Files:

- `base.py` — `YtDlpRunner` with `build_cmd(config, overrides) -> list[str]` and `run(cmd, on_progress) -> RunResult`. Single source of truth for cookies args, aria2c args, retries, timeouts, progress parsing. Reuses existing logic from `video_processor._build_yt_dlp_download_cmd` and `_run_yt_dlp_with_progress`.
- `router.py` — `resolve(url) -> BaseHandler`. Regex-based platform detection. Falls back to `GenericHandler`.
- `youtube.py`, `tiktok.py`, `instagram.py`, `vk.py`, `telegram.py`, `rutube.py`, `twitter.py`, `generic.py` — declarative handler configs (primary config + ordered fallback list). Each handler knows: format selector, player_client (YouTube), user-agent, whether cookies are required, which error codes trigger which fallback.
- `service.py` — `DownloadService.download(url, on_progress) -> DownloadResult` where `DownloadResult = { path: Path, platform: str, attempts: int, duration_s: float, format: str }`. Public API for `VideoProcessor`.
- `errors.py` — re-exports / extends `app/services/video_download_errors.py` with `retryable: bool` and `hint_action` enum.

`VideoProcessor.download_video()` becomes a thin wrapper calling `DownloadService.download()` so external callers (Celery tasks, tests) keep working.

### Model Warmup

`backend/app/services/model_manager.py`: add `async warmup_async()` invoked from FastAPI startup hook via `asyncio.create_task`. Sets `model_manager.is_warm = True` on completion. Failures are logged but do not abort startup. Reflected in `/health/ready`.

## Cookies Strategy

- Source of truth: `settings.YTDLP_COOKIES_FILE` (env). Default: `./backend/secrets/cookies/cookies.txt`.
- Folder `backend/secrets/cookies/` is added to `.gitignore` and mounted into Docker as `./backend/secrets:/app/secrets:ro`.
- Per-platform overrides: if `backend/secrets/cookies/cookies.<platform>.txt` exists (where `<platform>` ∈ `youtube`, `instagram`, `tiktok`, …), it overrides the shared file for that platform only.
- `Preflight` reports cookies presence per must-have platform (warnings, not critical failures).
- README section "Where to get cookies": short instructions (Chrome extension → Netscape format → drop into folder).
- Browser-cookies-in-runtime (`--cookies-from-browser`) is removed for non-YouTube URLs to avoid DPAPI/keyring failures; documented as deprecated.

## Data Flow (Download)

1. Celery task → `VideoProcessor.process(url=...)` → `DownloadService.download(url, on_progress)`.
2. `router.resolve(url)` returns a handler (e.g. `YouTubeHandler`).
3. For each attempt in `handler.attempts`:
   1. `YtDlpRunner.build_cmd(handler.config, overrides)`.
   2. `YtDlpRunner.run(cmd, on_progress)` streams progress to `on_progress(percent, message)` (5% → 15% range, preserved from current behavior).
   3. On success → return `DownloadResult`.
   4. On failure: classify error; if matches handler's retry conditions, continue to next attempt; else raise.
4. All attempts exhausted → `DownloadError(code, user_message, hint_action, raw)` propagates to the analysis task; analysis status becomes `failed` with those fields surfaced through existing progress stream.

## Error Classification

Extend `app/services/video_download_errors.py`:

```python
class DownloadError(Exception):
    error_code: ErrorCode
    user_message: str
    hint_action: Literal["provide_cookies", "install_ffmpeg", "retry_later", "unsupported_url", "unknown"]
    retryable: bool
    raw: str
```

Existing classification rules stay. Each rule gets `hint_action` and `retryable`. UI maps `hint_action` to actionable copy (out of scope here — frontend reads the field).

## Progress Stream

No new wire format. Existing progress event gains optional fields:

```json
{ "progress": 12, "stage": "downloading", "attempt": 2, "message": "Retrying with safer settings" }
```

Frontend already renders `message`; `attempt` is additive and ignored by current frontend safely.

## Testing

### Unit tests (`backend/tests/unit/services/downloaders/`)

- `test_router.py` — each must-have platform URL resolves to the right handler; unknown URLs → `GenericHandler`.
- `test_<platform>_handler.py` for youtube/instagram/tiktok — handler config produces expected yt-dlp argv (snapshot-style); fallback list is applied in declared order.
- `test_runner.py` — progress parsing from mock stdout; error classification across all known patterns (bot-check, fragment, cookies, ffmpeg-missing, 403, 429, private, geo).
- `test_preflight.py` — each check passes/fails under mocked dependencies; concurrent execution still returns all results when one check times out.
- `test_cookies_resolution.py` — per-platform cookies override the shared file; missing file emits warning, not error.

### Integration tests (`backend/tests/integration/`)

- `test_health_endpoints.py` — `/health/live` always 200; `/health/ready` 503 when a critical check is mocked failed, 200 when all green.
- `test_download_service_offline.py` — mock `subprocess` to feed yt-dlp stdout sequences (bot-check → fallback → success). No network.

### Smoke tests (`backend/tests/smoke/`)

- Gated by env flag `RUN_NETWORK_TESTS=1`. Not in CI. One canonical URL per must-have platform, list lives in `tests/smoke/urls.json` so URLs can be rotated without code changes.

## Migration

- `VideoProcessor.download_video()` stays as a thin wrapper around `DownloadService`. External API unchanged.
- New env vars (optional): `MODELS_WARMUP_ON_START=true` (default true), `YTDLP_COOKIES_FILE` already exists.
- No database migrations.
- Docs updated:
  - `DEV_STARTUP.md` — replace per-component steps with one-command flow as primary path; per-component preserved as appendix.
  - `backend/README.md` — cookies section, healthcheck endpoints.
  - `docs/decision-log.md` — entry: "Downloader layer extracted from VideoProcessor; preflight/health endpoints added".
  - `docs/architecture-evolution.md` — same entry, architectural framing.

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Regression in downloads after refactor | Snapshot tests on yt-dlp argv; offline integration test with mocked stdout; manual smoke before merge |
| Cookies expire over weeks | Preflight logs cookies file age; README documents refresh cadence |
| Lazy warmup delays first analysis | Warmup runs in background; UI shows "Loading models" until `is_warm`; readiness not blocked |
| Healthcheck masks real errors | Each check returns its own status and raw message; no boolean aggregation |
| Preflight hangs on broken dependency | Per-check 5s timeout; failing check does not block sibling checks |
| Instagram requires login and cookies file is empty | Preflight warning at startup; handler emits `provide_cookies` hint on failure |

## Rollback

Plain `git revert` of the merge commit. No fence-posted feature flag — refactor preserves the public contract, and new endpoints are additive.

## Governance Compliance

- `AGENTS.md`: preserve current behavior ✓; move-before-rewrite ✓; backward-compatible API ✓; tests for changed behavior ✓; docs updated ✓; rollback documented ✓.
- `docs/engineering-laws.md`: smallest working change first ✓; observability touchpoints (`/health/ready` per-check status + structured logs in runner) ✓.
- `docs/architecture-evolution.md`: documented architectural decision.

## Out of Scope (Explicit)

- B (dataset completion) and C (design/UX upgrade) — separate spec → plan cycles.
- Brand detection quality, ad classifier tuning.
- Frontend visual changes beyond surfacing existing `message` and new `hint_action` text.
- Production deployment (Railway/Vercel) infra changes.
