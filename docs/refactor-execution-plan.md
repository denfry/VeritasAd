# Refactor Execution Plan

## Strategy

Use move-before-rewrite with behavior parity at each step.

## Phased Plan

1. Baseline current behavior and critical contracts.
2. Extract route-level business logic into domain services/use-cases where missing.
3. Consolidate duplicate endpoints and keep compatibility shims.
4. Introduce shared contract schemas for progress/results/report metadata.
5. Reduce oversized modules through bounded extractions.

## Safety Controls

- test-first for changed modules
- per-step rollback instructions
- migration compatibility checks for DB/env/API
- no multi-domain rewrites in one PR

## Dead Code Strategy

- deprecate with warning period
- remove only after usage confirmation and release note entry
