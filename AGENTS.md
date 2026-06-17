# AGENTS.md - VeritasAd Repository Operating System

VeritasAd is a neural network-based advertising detection platform (FastAPI backend + Next.js frontend) with async video processing, compliance evidence extraction, and report generation.

## Mandatory Governance Contract

These files are mandatory operating rules for every future task in this repository:

1. `AGENTS.md` (this file)
2. `docs/engineering-laws.md`
3. `docs/architecture-evolution.md`
4. `docs/structure-governance.md`
5. `docs/release-governance.md`
6. `docs/tech-debt-system.md`
7. `docs/ai-learning-loop.md`
8. `docs/execution-checklists.md`
9. `.ai/workflows/*.md`

If any instruction conflicts, apply the most restrictive rule that preserves behavior, safety, and compatibility.

## Product Direction (Inferred)

- Primary product: ad/compliance intelligence for video and social content.
- Core value: detect promotional signals (visual/audio/disclosure/link), produce explainable verdicts, and export evidence-ready reports.
- Commercial direction: self-hosted + SaaS hybrid, with subscriptions, pay-as-you-go credits, and API usage.
- Growth vectors: enterprise compliance workflows, partner ingestion pipelines, and scalable asynchronous processing.

## Non-Negotiable Engineering Rules

- Preserve current behavior unless a task explicitly requests behavior change.
- Prefer move-before-rewrite for structural changes.
- Keep public API contracts backward compatible unless versioned.
- Never blend unrelated refactors with feature work.
- Every risky change must include rollback instructions.
- Every code change must update linked docs when behavior/contracts/config change.
- No speculative rewrites of business logic.

## Deterministic Change Policy

- Define scope, touched modules, and compatibility expectations before editing.
- Minimize blast radius: smallest working change first.
- Add or update tests for changed behavior.
- Include observability touchpoints for critical path changes.
- Record architectural decisions in `docs/decision-log.md`.

## Branch, Commit, and PR Discipline

- Branch prefixes: `feature/*`, `fix/*`, `refactor/*`, `hotfix/*`, `release/*`, `docs/*`.
- Commit format: `type(scope): short description`.
- PR must include:
  - purpose and impact area
  - migration/rollback notes (if applicable)
  - test evidence
  - documentation delta

## Compatibility Guarantees

- Keep endpoints, payload fields, and env vars stable by default.
- Database migrations must be additive-first and reversible when feasible.
- Preserve report formats and downstream integrations unless explicitly versioned.
- Preserve queue task contracts and progress events consumed by frontend.

## Commands

### Frontend (`frontend/`)

```bash
npm run dev
npm run build
npm run start
npm run lint
npm run type-check
```

No frontend test runner is configured.

### Backend (`backend/`)

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
alembic revision --autogenerate -m "desc"
alembic upgrade head
uv run pytest
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest --cov=app
```

### Formatting and Linting

```bash
uv run black backend/
uv run ruff check backend/
uv run ruff check --fix backend/
uv run mypy backend/app/
cd frontend && npm run lint
pre-commit run --all-files
```

## Architecture and Ownership Snapshot

- Backend domains (`backend/app/domains/*`) are the primary business boundaries.
- Async analysis pipeline (`backend/app/tasks/video_analysis.py`) is release critical.
- API client contract (`frontend/src/lib/api-client.ts`) is frontend-backend contract-critical.
- Config and limits (`backend/app/core/config.py`) are high-change and high-risk.

## Research Workspace

Research artifacts for the two academic tracks (VeritasAd 2.0 master's, VeritasAd 3.0 PhD) live under
`docs/research/`, organized by artifact type (roadmaps / prompts / plans / specs / reports / experiments /
datasets / literature), each split into `master/` and `phd/` phases.

- Entry point and conventions: [`docs/research/README.md`](docs/research/README.md) (naming, frontmatter,
  status lifecycle, milestone map, path-correspondence table).
- Templates for every artifact type: `docs/research/_templates/`.
- Dataset **documentation** (JSONL schemas, annotation guidelines) lives in `docs/research/datasets/`;
  the **data itself** lives in `data/datasets/` (raw/large files are git-ignored there).
- Same governance rules apply: preserve behavior, move-before-rewrite, keep linked docs in sync,
  `docs/*` branches, `type(scope): ...` commits.

## Document and Git Synchronization Rules

For every code change, validate related artifacts:

- `README` and setup docs
- architecture docs (`docs/current-architecture-map.md`, `docs/target-architecture.md`)
- release docs (`docs/changelog.md`, `docs/release-notes.md`, migration/rollback docs)
- API/user-facing docs if routes/contracts changed

For every document change, validate referenced commands, paths, and compatibility claims.

## Release Safety Defaults

- Feature flags for risky/large behavior changes.
- Canary or phased rollout for critical path changes.
- Rollback path must exist before release approval.
- Post-incident updates must feed back into rules and checklists.

## Tech Stack Notes

- Backend package manager: `uv`
- Frontend package manager: `npm`
- Python: `>=3.12,<3.13`
- Auth: Supabase + JWT flows
- Background processing: Celery + Redis
- Observability: OpenTelemetry + Sentry + structlog
