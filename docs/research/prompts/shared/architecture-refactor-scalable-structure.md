You are a principal software architect, repository modernization expert, and large-scale refactor strategist.

Your task is to inspect the CURRENT EXISTING project structure, understand all present logic and business flows, and transform the repository into a clean, scalable, maintainable, and understandable architecture WITHOUT breaking current behavior.

CRITICAL RULE:
Do NOT redesign blindly.
You must first understand the existing architecture, logic, dependencies, data flows, and implicit design decisions.

==================================================
PHASE 1 — REPOSITORY DISCOVERY
==================================================

Inspect and document:

- current folder structure
- package/module boundaries
- service responsibilities
- duplicated logic zones
- god classes
- utility misuse
- cyclic dependencies
- config structure
- entry points
- public interfaces
- database access flow
- event flow
- async/background tasks
- external integrations
- business-critical modules
- high-change files
- technical debt hotspots

Create:
- docs/current-architecture-map.md
- docs/problematic-areas.md
- docs/scaling-risks.md

==================================================
PHASE 2 — STRUCTURAL ANALYSIS
==================================================

Identify:

- weak boundaries
- mixed responsibilities
- business logic in controllers/UI
- poor naming
- deep nesting
- bad package cohesion
- hidden side effects
- duplicated services
- scattered config handling
- broken abstraction layers
- missing domain separation
- test-hostile structure
- poor extension points
- plugin-unfriendly design

Prioritize by:
1) business risk
2) scaling pain
3) onboarding complexity
4) bug frequency
5) future feature cost

==================================================
PHASE 3 — TARGET SCALABLE STRUCTURE
==================================================

Design a future-proof repository structure.

Goals:
- easy onboarding
- clear folder naming
- predictable module placement
- feature-oriented scalability
- low coupling
- high cohesion
- test-friendly layout
- plugin/extensibility ready
- async-safe boundaries
- migration-safe modules
- API-safe contracts
- reusable shared core

Generate:
- docs/target-architecture.md
- docs/module-boundaries.md
- docs/scaling-strategy.md

==================================================
PHASE 4 — SAFE REFACTOR STRATEGY
==================================================

Create:
docs/refactor-execution-plan.md

Must include:
- step-by-step migration plan
- minimal blast-radius edits
- move-before-rewrite strategy
- test-first verification
- dependency untangling order
- config compatibility plan
- API compatibility plan
- DB compatibility plan
- rollback path
- safe rename workflow
- dead code elimination strategy

==================================================
PHASE 5 — NEW REPOSITORY STRUCTURE
==================================================

Generate a new clean scalable structure based on detected stack.

Rules:
- preserve behavior
- preserve entry points
- preserve public APIs
- preserve config compatibility
- isolate domain logic
- isolate infrastructure
- isolate interfaces
- isolate data access
- isolate workflows/use cases
- isolate shared utilities
- isolate integrations
- isolate feature modules

Prefer:
- feature-first modules
OR
- clean architecture layers
depending on current project growth path

==================================================
PHASE 6 — GOVERNANCE RULES
==================================================

Generate:
docs/structure-governance.md

Rules must define:
- where new files go
- how modules evolve
- max module responsibility
- dependency direction
- naming rules
- feature module template
- service extraction thresholds
- when shared utils are allowed
- anti-god-class limits
- anti-circular dependency rules

==================================================
PHASE 7 — SELF-SCALING EVOLUTION
==================================================

Generate:
docs/future-growth-plan.md

Define:
- when to split modules
- when to extract services
- when to move to microservices/plugins
- how to handle growing config
- how to evolve DB access
- how to isolate high-load paths
- how to introduce caching layers
- how to scale async workloads
- how to add extension APIs

==================================================
FINAL REQUIREMENTS
==================================================

The final structure must be:
- readable by new developers
- easy to navigate
- safe for large feature growth
- optimized for refactors
- optimized for testing
- optimized for release safety
- optimized for long-term maintainability
- stack-aware
- technology-agnostic
- resistant to architecture drift

Output:
1) current structure analysis
2) target scalable structure tree
3) migration roadmap
4) risk zones
5) governance rules
6) future scaling strategy