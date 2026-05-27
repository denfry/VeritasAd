# Local Env + Universal Video Download — Implementation Plan

**Spec:** `docs/superpowers/specs/2026-05-27-local-env-video-download-design.md`
**Executor:** Codex (external)
**Goal:** Deliver sub-project A from the spec. Codex is expected to grep the repo, read referenced files, and make judgment calls. This plan lists tasks and acceptance, not step-by-step code.

**Tech:** FastAPI, Celery, yt-dlp, Docker Compose, pytest, PowerShell + Bash scripts.

**Ground rules:**
- TDD where reasonable (handler configs, error classifier, preflight checks).
- Keep `VideoProcessor.process()` and `VideoProcessor.download_video()` public contracts.
- Small commits per task. Conventional commit format (`feat(downloader): …`, `refactor(video): …`, `chore(local): …`).
- Update docs in the same PR as the code change.

---

## Task 1 — Error model

**Files:** `backend/app/services/video_download_errors.py` (modify), tests under `backend/tests/unit/`.

Introduce `DownloadError(Exception)` with fields `error_code`, `user_message`, `hint_action` (`Literal["provide_cookies","install_ffmpeg","retry_later","unsupported_url","unknown"]`), `retryable: bool`, `raw: str`. Extend `classify_processing_error` to also return `hint_action` and `retryable`. Keep existing string keys for backward compat. Unit-test each existing rule + a new "unsupported_url" rule.

**Done when:** all existing call sites still get `error_code` and `user_message`; new fields are populated; tests cover every branch.

---

## Task 2 — Downloader layer scaffold

**Files (new):** `backend/app/services/downloaders/{__init__,base,router,service,errors,handlers/{youtube,tiktok,instagram,vk,telegram,rutube,twitter,generic}}.py`.

- `base.YtDlpRunner`: build argv (cookies, aria2c, retries, geo-bypass, format, player-client, UA) and run with line-by-line progress parsing. Lift the logic from `video_processor._build_yt_dlp_download_cmd` and `_run_yt_dlp_with_progress` verbatim, then parameterize.
- `handlers/*`: declarative `HandlerConfig` (primary + ordered fallbacks). YouTube fallbacks = current `safer_attempts`. Instagram primary requires cookies and warns if missing. TikTok fallback swaps UA. Generic = bare yt-dlp.
- `router.resolve(url) -> Handler` via regex; default = generic.
- `service.DownloadService.download(url, on_progress) -> DownloadResult` orchestrates handler attempts, classifies errors via Task 1, raises `DownloadError` after exhausting fallbacks.
- `errors.py` re-exports `DownloadError` and helpers.

**Tests:** `backend/tests/unit/services/downloaders/`
- `test_router.py`: each must-have platform URL resolves correctly; unknown → generic.
- `test_handlers.py`: argv snapshot per handler primary + each fallback.
- `test_runner.py`: progress parsing from mock stdout; subprocess mocked.
- `test_service.py`: integration of router + handler + runner with mocked subprocess: bot-check → fallback → success; all-fail → `DownloadError` with correct `hint_action`.

**Done when:** new package has > 90% line coverage; no network calls in tests.

---

## Task 3 — Wire DownloadService into VideoProcessor

**Files:** `backend/app/services/video_processor.py` (modify).

Replace the body of `download_video` and `get_url_metadata`'s yt-dlp call with `DownloadService.download(...)`. Keep method signatures and return types identical. Delete now-dead helpers (`_build_yt_dlp_download_cmd`, `_run_yt_dlp_with_progress`, `_is_youtube_*`, `_is_fragment_*`, `_is_cookie_*`, `_is_ffmpeg_*`, `_build_auth_args`) — they live in the downloader package now.

**Done when:** existing tests in `backend/tests/unit/test_*.py` that exercise download paths still pass with mocks pointed at the new package.

---

## Task 4 — Per-platform cookies resolution

**Files:** `backend/app/services/downloaders/base.py`, `backend/app/core/config.py`.

`YtDlpRunner` picks cookies in order: `cookies.<platform>.txt` next to `YTDLP_COOKIES_FILE` → `YTDLP_COOKIES_FILE` itself → none. Remove `--cookies-from-browser` path for non-YouTube URLs (kept as deprecated/log-warned for YouTube only, since runtime cookie decryption is documented-broken).

Add `.gitignore` entries for `backend/secrets/cookies/`. Mount in `docker-compose.local.yml` as `./backend/secrets:/app/secrets:ro` and set `YTDLP_COOKIES_FILE=/app/secrets/cookies/cookies.txt` env in backend + celery-worker services.

**Tests:** unit test for the resolution order.

---

## Task 5 — Preflight module + health endpoints

**Files (new):** `backend/app/core/preflight.py`. **Modify:** `backend/app/domains/health/router.py`, `docker-compose.local.yml` (healthcheck blocks).

`Preflight.run_checks()` concurrently runs: `ffmpeg`/`ffprobe` via `shutil.which`; `yt_dlp` import; cookies file presence and age; Redis ping; DB `SELECT 1`; data dirs writable; `model_manager.is_warm`. Each check has a 5s timeout. Results cached 30s. Each returns `{name, status: ok|warning|failed, message, duration_ms}`.

Endpoints (mounted under existing `/api/v1`):
- `GET /health/live` — `{ok: true}`, no checks.
- `GET /health/ready` — full result; HTTP 503 if any critical check failed.

Mark cookies + `models_warm` as non-critical (warning).

Existing `GET /health` keeps current behavior to preserve consumers.

**Tests:** mock each dependency; assert critical-failure → 503; warning-only → 200.

---

## Task 6 — Async model warmup

**Files:** `backend/app/services/model_manager.py`, `backend/app/main.py` (startup hook).

Add `async warmup_async()` and `is_warm: bool` flag. On FastAPI startup, schedule `asyncio.create_task(model_manager.warmup_async())` guarded by env `MODELS_WARMUP_ON_START` (default true). Log progress; on failure log and leave `is_warm = False` — never abort startup.

**Tests:** existing model_manager tests still pass; new test verifies `is_warm` flips after `warmup_async()` succeeds.

---

## Task 7 — Bootstrap scripts

**Files (new):** `scripts/local-up.ps1`, `scripts/local-up.sh`, `scripts/local-down.ps1`, `scripts/local-down.sh`, `Makefile` (modify or create).

`local-up`:
1. For each `.env.example` (root, backend, frontend) — if matching `.env` missing, copy. Print which were copied.
2. `docker compose -f docker-compose.local.yml up -d`.
3. Poll `GET http://localhost:8000/api/v1/health/ready` every 3s up to 120s.
4. Print URL table + per-check status. Exit 0 when ready, exit 1 on timeout (and print last response).

`local-down`: `docker compose -f docker-compose.local.yml down`.

`Makefile`: targets `local`, `local-down` wrapping the `.sh` scripts.

Idempotent. Both scripts must work on a freshly-cloned repo.

---

## Task 8 — Progress event enrichment

**Files:** `backend/app/services/downloaders/service.py`, callers in `backend/app/tasks/video_analysis.py` (and wherever `on_progress` flows).

Existing progress callback `(int, str)` is preserved. Where progress events become a dict (Celery task / progress stream), add optional `attempt: int` and `stage: "downloading"` fields. Frontend already tolerates unknown fields. No frontend change required for this task.

---

## Task 9 — Smoke tests (gated)

**Files (new):** `backend/tests/smoke/test_real_downloads.py`, `backend/tests/smoke/urls.json`.

Skip unless `RUN_NETWORK_TESTS=1`. One canonical URL per must-have platform in `urls.json`. Each test calls `DownloadService.download(url, ...)` and asserts a file was produced and is non-empty. Network calls excluded from default `pytest` run via marker `@pytest.mark.smoke` plus default `--deselect` in `pyproject.toml`.

---

## Task 10 — Docs

**Files:** `DEV_STARTUP.md`, `backend/README.md`, `docs/decision-log.md`, `docs/architecture-evolution.md`.

- `DEV_STARTUP.md`: lead with the one-command flow; current per-component instructions move to an appendix.
- `backend/README.md`: cookies section (where to put files, per-platform overrides, refresh cadence) + healthcheck endpoints.
- `docs/decision-log.md` + `docs/architecture-evolution.md`: short entries about the downloader-layer extraction and preflight endpoints.

---

## Verification before "done for A"

- `pytest backend/tests` green.
- `./scripts/local-up.ps1` on a clean clone prints `READY` ≤ 120s.
- `curl /api/v1/health/ready` shows all critical checks ok.
- With a valid `cookies.youtube.txt`, smoke test for YouTube passes locally.
- `VideoProcessor.process(url=...)` end-to-end succeeds for one URL per must-have platform (manual check, cookies provided where required).
- `git grep -n "TBD\|TODO" docs/superpowers` returns no new entries.

## Out of scope here

Anything from sub-projects B (dataset completion) and C (design/UX). Brand/ad detection quality. Production infra changes.
