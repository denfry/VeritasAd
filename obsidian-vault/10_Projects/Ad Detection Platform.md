---
title: Ad Detection Platform
created: 2026-05-27
tags: [veritasad, product]
status: active
related: ["[[Home]]", "[[ML And Analysis Pipeline]]", "[[Backend]]"]
---

# Ad Detection Platform

VeritasAd detects promotional signals in video and social content and produces explainable, evidence-ready reports.

## Product Value

- Detect visual, audio, disclosure, and link-based promotional signals.
- Explain verdicts with evidence that can support compliance workflows.
- Support async video analysis, partner ingestion, and exportable reports.

## Core Implementation Surfaces

- Backend domains: [backend/app/domains](../../backend/app/domains)
- Async video analysis: [video_analysis.py](../../backend/app/tasks/video_analysis.py)
- Frontend API client: [api-client.ts](../../frontend/src/lib/api-client.ts)
- Config and limits: [config.py](../../backend/app/core/config.py)

## Related

- [[Backend]]
- [[Frontend]]
- [[ML And Analysis Pipeline]]
