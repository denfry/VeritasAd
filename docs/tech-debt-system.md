# Tech Debt System

## Debt Hotspots (Current)

- Large multi-responsibility modules in analysis and admin domains.
- Duplicate/legacy API surfaces under both `api/v1/*` and `domains/*` paths.
- Sparse frontend automated tests.
- High volatility in config and API client layers.

## Debt Classification

- Critical: causes data loss, security gap, severe regression risk.
- High: materially slows delivery or repeatedly causes defects.
- Medium: local maintainability pain with bounded risk.
- Low: cosmetic or isolated structural debt.

## Prioritization Model

Priority score = business risk x change frequency x blast radius x recovery cost.

## Repayment Policy

- 20 percent of each sprint capacity reserved for debt on critical paths.
- Every recurring defect class must produce a rule, test, and checklist update.
- Debt can be deferred only with documented expiry and owner.

## Acceptable Debt

Allowed when:

- temporary workaround is time-boxed,
- rollback is clear,
- monitoring detects failure quickly,
- follow-up ticket is linked to roadmap.

## Recurrence Prevention

- Track repeated review comments and incidents.
- Convert top repeated patterns into lint checks, templates, or workflow gates.
