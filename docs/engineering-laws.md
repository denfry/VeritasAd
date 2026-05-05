# Engineering Laws

## Purpose

Universal engineering laws for maintaining VeritasAd as a scalable, testable, and low-risk system.

## Law Set

1. Simplicity threshold: choose the simplest design that satisfies current requirements and explicit near-term roadmap.
2. Complexity budget: reject changes that increase branching, indirection, or coupling without measurable business gain.
3. Abstraction constraint: extract abstractions only after two real call sites or one proven volatility hotspot.
4. Coupling ceiling: domain modules may depend inward (core/shared) but not sideways through hidden imports.
5. Duplication tolerance: small tactical duplication is acceptable if it prevents premature shared abstractions.
6. Module size governance: split files when responsibility broadens, not only by line count.
7. Naming law: names must express business intent, not implementation detail.
8. Error propagation law: propagate typed domain errors; avoid generic exception swallowing.
9. Logging law: emit structured logs with identifiers and stage context, no sensitive payload leakage.
10. Observability law: every critical path stage must be traceable (request id, task id, status transitions).
11. Testability law: business logic should be callable without HTTP or UI harnesses.
12. Maintainability score: each PR must improve or preserve readability, boundary clarity, and rollback confidence.

## Quantitative Heuristics

- Public endpoint change requires:
  - compatibility decision (`compatible`, `versioned`, or `breaking`)
  - updated API/client docs
- Any migration touching non-null or enum contracts requires rollback strategy.
- Any async pipeline change requires progress and failure-path verification.
