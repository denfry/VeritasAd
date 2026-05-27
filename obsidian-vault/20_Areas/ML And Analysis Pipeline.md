---
title: ML And Analysis Pipeline
created: 2026-05-27
tags: [ml, analysis, video]
status: active
related: ["[[Ad Detection Platform]]", "[[Backend]]", "[[Architecture]]"]
---

# ML And Analysis Pipeline

The ML and analysis pipeline turns video and social inputs into promotional-signal evidence and explainable verdicts.

## Key Paths

- [backend/app/tasks/video_analysis.py](../../backend/app/tasks/video_analysis.py)
- [backend/app/ml](../../backend/app/ml)
- [backend/app/services/video_processor.py](../../backend/app/services/video_processor.py)
- [backend/app/services/social_parsers.py](../../backend/app/services/social_parsers.py)
- [backend/app/services/link_detector.py](../../backend/app/services/link_detector.py)
- [docs/ml-ad-detection.md](../../docs/ml-ad-detection.md)

## Guardrails

- Preserve async task contracts consumed by frontend progress UI.
- Keep evidence fields stable unless a migration and compatibility path are explicit.
- Add tests for changes to scoring, extraction, parsing, and report behavior.

## Related

- [[Ad Detection Platform]]
- [[Backend]]
- [[Architecture]]
