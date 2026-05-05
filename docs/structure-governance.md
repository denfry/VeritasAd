# Structure Governance

## File Placement Rules

- domain logic goes under `backend/app/domains/<domain>`
- infra adapters go under `backend/app/platform` or `backend/app/integrations`
- cross-domain contracts go under `backend/app/contracts`
- frontend feature code belongs in `frontend/src/features/<feature>` (incremental adoption)

## Dependency Direction

- interface -> application -> infrastructure
- no inward dependency from core/platform to feature domains

## Extraction Thresholds

Extract module/service when:

- module handles 3+ independent responsibilities
- change frequency is high and ownership unclear
- test setup complexity indicates hidden coupling

## Anti-God-Class Limits

- avoid adding unrelated concerns to existing large modules
- split by business capability, not helper type

## Circular Dependency Rules

- circular imports are release blockers
- resolve by introducing explicit interface modules
