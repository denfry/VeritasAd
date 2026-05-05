# Scaling Risks

## Operational Risks

- queue saturation under high video load
- storage pressure from artifact retention
- database contention as analytics/admin queries grow
- websocket/sse fanout limits for progress streaming

## Architecture Risks

- oversized modules reduce safe parallel development
- domain boundary erosion increases coupling and regression risk
- insufficient contract tests between frontend and backend

## Product Risks

- billing and credits complexity can drift without contract checks
- compliance/report semantics can regress without golden samples

## Mitigations

- stage-level observability and SLOs
- workload isolation for heavy pipeline tasks
- contract test suite for API and progress payloads
- explicit module ownership and extraction thresholds
