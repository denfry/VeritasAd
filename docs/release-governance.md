# Release Governance

## Release Checklist

- scope and impact documented
- backward compatibility validated
- migrations reviewed and reversible where possible
- docs/changelog/release notes updated
- tests and smoke checks passed
- observability and alerts in place

## Compatibility Gates

- API payload compatibility checked against frontend client usage.
- Progress stream/event payload compatibility validated.
- Env var changes include defaults and migration notes.

## Feature Flag Rules

- High-risk behavior changes must be flaggable.
- Flags require owner, expiry date, and rollback behavior.

## Rollback Rules

- Every release has explicit rollback path and data impact statement.
- Rollback drills required for migration-heavy releases.

## Canary Strategy

- Use phased rollout for pipeline and billing/security changes.
- Monitor error rate, latency, queue depth, and failure stages before full rollout.

## Incident Workflow

1. detect and triage severity
2. contain blast radius
3. recover service
4. publish incident summary
5. convert root causes into permanent controls

## Hotfix Workflow

- isolate minimal patch
- run targeted tests
- deploy with rollback readiness
- post-hotfix retrospective within 24 hours

## Postmortem Template

- timeline
- impact
- root causes
- detection gaps
- prevention actions
- owners and due dates
