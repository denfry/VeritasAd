---
title: Frontend
created: 2026-05-27
tags: [frontend, nextjs, veritasad]
status: active
related: ["[[Architecture]]", "[[Command Reference]]"]
---

# Frontend

The frontend owns the user workflows for analysis, pricing, account surfaces, legal pages, documentation, and metadata.

## Key Paths

- [frontend/src/app](../../frontend/src/app)
- [frontend/src/components](../../frontend/src/components)
- [frontend/src/lib/api-client.ts](../../frontend/src/lib/api-client.ts)
- [frontend/src/lib/seo-config.ts](../../frontend/src/lib/seo-config.ts)

## Contracts

- Treat `frontend/src/lib/api-client.ts` as a frontend-backend contract surface.
- Preserve route behavior and metadata unless a task explicitly changes them.

## Related

- [[Architecture]]
- [[Backend]]
- [[Command Reference]]
