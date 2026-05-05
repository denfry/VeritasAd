# Architecture Evolution

## Current Architecture Map (Summary)

- Frontend: Next.js App Router with a self-hosted-first UX and API-driven analysis workspace.
- Backend: FastAPI with domain routers, service layer, async SQLAlchemy, Redis, Celery tasks.
- Pipeline: intake -> download/normalize -> multimodal analysis -> scoring/classification -> report export.
- Integrations: Supabase auth, YooKassa payments, Telegram linking, social source parsing.

## Target Architecture Direction

- Preserve monorepo.
- Strengthen feature/domain boundaries in backend and frontend.
- Move toward explicit contracts between:
  - interface layer (routers/pages)
  - application services/use-cases
  - infrastructure adapters (DB, Redis, external APIs)

## Evolution Milestones

1. Stabilize contracts and reduce duplication in analysis/progress/report routes.
2. Isolate pipeline stages into composable workers with explicit handoff schemas.
3. Harden observability and failure handling per stage.
4. Enable partner/plugin-style ingestion adapters.
5. Prepare optional service decomposition only after scale thresholds are met.

## Bounded Contexts

- Analysis and evidence extraction
- Reporting and exports
- Users and auth
- Billing and credits
- Security and sessions
- Administration and audit
- Integrations (Telegram/social providers)

## Service Decomposition Rules

- Decompose only when one of these holds:
  - independent scaling profile
  - independent release cadence
  - operational isolation requirement
- Keep API compatibility layer stable during decomposition.

## State Ownership

- Durable business state: PostgreSQL.
- Ephemeral progress and coordination: Redis.
- Large artifacts: file storage/S3-compatible target.

## Versioning Contracts

- API: additive first; breaking changes via versioned routes.
- Events/progress payloads: schema version field when changing shape.
- DB: forward migration + explicit rollback notes.
