# Execution Checklists

## PRE-CODE

- business goal and constraints clear
- impacted modules identified
- compatibility and rollback assumptions documented
- test strategy defined

## PRE-MERGE

- no unrelated changes
- tests and lint/type checks pass
- docs and changelog updated
- migration and rollback notes included

## PRE-RELEASE

- release notes complete
- feature flags and monitors configured
- blast radius estimated
- on-call and rollback owner assigned

## POST-INCIDENT

- root cause documented
- customer impact quantified
- prevention actions created
- rules/checklists/workflows updated

## POST-MIGRATION

- data integrity validated
- performance baseline compared
- rollback feasibility re-verified

## PERFORMANCE-REVIEW

- p95/p99 latency trends reviewed
- queue depth and worker saturation reviewed
- hot paths and cache efficacy reviewed

## SECURITY-REVIEW

- auth/session/webhook paths reviewed
- sensitive data exposure checks passed
- dependency vulnerabilities triaged

## ARCHITECTURE-DRIFT

- module boundaries still respected
- coupling and ownership drift identified
- extraction/decomposition triggers evaluated
