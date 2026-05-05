# Module Boundaries

## Boundary Rules

- Routers call use-cases/services, not raw infrastructure logic.
- Domain use-cases own business rules and orchestration.
- Repositories own persistence concerns only.
- Integrations are adapter modules behind stable interfaces.
- Shared utilities are allowed only for cross-domain generic behavior.

## Forbidden Patterns

- business logic in API routers or UI pages
- cross-domain imports that bypass interfaces
- global utility dumping for domain-specific helpers

## Ownership Template

Each domain must define:

- purpose
- public interface
- dependency rules
- test coverage expectations
- observability events
