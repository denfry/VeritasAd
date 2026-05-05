# Problematic Areas

## Highest-Risk Structural Zones

1. Analysis pipeline orchestration spans large files and mixed responsibilities.
2. Admin domain router is broad and likely hard to evolve safely.
3. Duplicate or legacy API surfaces suggest boundary drift.
4. Frontend API client is high-change and contract-sensitive.
5. Config layer carries many product and infra toggles in one place.

## Symptoms

- broad modules with high cognitive load
- repeated touch points in config/client layers
- hidden coupling between progress/events and frontend assumptions
- uneven test depth across domains

## Impact

- slower onboarding
- higher regression risk in release-critical flows
- higher maintenance cost for new feature delivery
