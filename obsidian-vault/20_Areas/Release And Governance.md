---
title: Release And Governance
created: 2026-05-27
tags: [release, governance]
status: active
related: ["[[VeritasAd Operating System]]", "[[Command Reference]]", "[[Decision Log Index]]"]
---

# Release And Governance

Release governance keeps VeritasAd deployable, reversible, and compatible with downstream consumers.

## Canonical Docs

- [release-governance.md](../../docs/release-governance.md)
- [release-notes.md](../../docs/release-notes.md)
- [changelog.md](../../docs/changelog.md)
- [rollback-guide.md](../../docs/rollback-guide.md)
- [migration-guide.md](../../docs/migration-guide.md)
- [execution-checklists.md](../../docs/execution-checklists.md)

## Checklist

- Include purpose, impact area, migration and rollback notes, test evidence, and documentation delta.
- Keep database migrations additive-first and reversible when feasible.
- Do not merge risky behavior without observability touchpoints.

## Related

- [[VeritasAd Operating System]]
- [[Decision Log Index]]
- [[Command Reference]]
