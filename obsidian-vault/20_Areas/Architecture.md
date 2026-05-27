---
title: Architecture
created: 2026-05-27
tags: [architecture, veritasad]
status: active
related: ["[[Backend]]", "[[Frontend]]", "[[ML And Analysis Pipeline]]"]
---

# Architecture

VeritasAd architecture centers on a FastAPI backend, Next.js frontend, async analysis pipeline, and evidence-oriented reporting.

## Canonical Architecture Docs

- [current-architecture-map.md](../../docs/current-architecture-map.md)
- [target-architecture.md](../../docs/target-architecture.md)
- [module-boundaries.md](../../docs/module-boundaries.md)
- [scaling-strategy.md](../../docs/scaling-strategy.md)
- [scaling-risks.md](../../docs/scaling-risks.md)

## Watch Points

- Backend domains are the business boundaries.
- Queue contracts and progress events are frontend-facing contracts.
- Config, limits, report schemas, and API client types are high-risk change points.

## Related

- [[Backend]]
- [[Frontend]]
- [[ML And Analysis Pipeline]]
- [[Decision Log Index]]
