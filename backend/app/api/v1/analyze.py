"""Backward-compatible analysis helper exports.

The analysis implementation lives under `app.domains.analysis`; this module
keeps legacy imports working for tests and integrations that still reference
`app.api.v1.analyze`.
"""

from app.domains.analysis.analyze_router import is_safe_url
from app.domains.analysis.service import _has_video_payload, _infer_source_type

__all__ = ["_has_video_payload", "_infer_source_type", "is_safe_url"]
