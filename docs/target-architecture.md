# Target Architecture

## Target Principles

- feature/domain-first modular monolith
- strict interface -> application -> infrastructure boundaries
- explicit contracts for API, events, and reports
- observability-first critical paths

## Proposed Structure (Conceptual)

- `backend/app/domains/<domain>`: routers + schemas + use-cases + repositories
- `backend/app/platform`: shared infrastructure (db, redis, auth, telemetry)
- `backend/app/integrations`: external providers (social, payment, messaging)
- `backend/app/contracts`: API/event/report schemas
- `frontend/src/features/<feature>`: pages, components, hooks by feature

## Why This Direction

- keeps current deployment model intact
- improves onboarding and ownership clarity
- supports gradual extraction to services/plugins when justified
