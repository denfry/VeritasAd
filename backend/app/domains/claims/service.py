"""Claims domain service (VeritasAd 2.0, M2).

Business layer for on-demand claim extraction. Wraps
:class:`app.services.claim_extractor.ClaimExtractor` and bridges it to stored
analyses: it reads the multimodal signals already persisted on an
:class:`~app.models.database.Analysis`, runs extraction with the requesting
user's LLM plan, and (optionally) persists the result onto ``Analysis.claims``.

Persistence is additive and behaviour-preserving: a stored result is only written
when explicitly requested, and reading claims never triggers analysis side effects.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.models.database import Analysis, UserPlan
from app.schemas.claims import (
    ClaimExtractionRequest,
    ClaimExtractionResult,
    ExtractionMethod,
)
from app.services.claim_extractor import ClaimExtractor

logger = logging.getLogger(__name__)


def _coerce_plan(plan: Any) -> UserPlan:
    """Coerce a stored/str plan onto the UserPlan enum, defaulting to FREE."""
    if isinstance(plan, UserPlan):
        return plan
    try:
        return UserPlan(str(plan))
    except (ValueError, TypeError):
        return UserPlan.FREE


class ClaimsService:
    """Service for verifiable advertising claim extraction."""

    def __init__(self, extractor: Optional[ClaimExtractor] = None) -> None:
        self.extractor = extractor or ClaimExtractor()

    async def extract(
        self, request: ClaimExtractionRequest, *, plan: "UserPlan | str" = UserPlan.FREE
    ) -> ClaimExtractionResult:
        """Extract claims from a raw request."""
        return await self.extractor.extract(request, plan=_coerce_plan(plan))

    @staticmethod
    def request_from_analysis(
        analysis: Analysis, method: ExtractionMethod
    ) -> ClaimExtractionRequest:
        """Build an extraction request from the signals stored on an analysis."""
        return ClaimExtractionRequest(
            transcript=analysis.transcript or "",
            detected_brands=analysis.detected_brands or [],
            disclosure_markers=analysis.disclosure_markers or [],
            cta_matches=getattr(analysis, "cta_matches", None) or [],
            commercial_urls=getattr(analysis, "commercial_urls", None) or [],
            method=method,
            content_id=analysis.video_id,
            source_type=(
                analysis.source_type.value
                if hasattr(analysis.source_type, "value")
                else analysis.source_type
            ),
            source_url=analysis.source_url,
        )

    async def extract_from_analysis(
        self,
        *,
        analysis: Analysis,
        session: Any,
        method: ExtractionMethod = ExtractionMethod.RULE_BASED,
        persist: bool = True,
        plan: "UserPlan | str" = UserPlan.FREE,
    ) -> ClaimExtractionResult:
        """Extract claims from a stored analysis, optionally persisting the result."""
        request = self.request_from_analysis(analysis, method)
        result = await self.extractor.extract(request, plan=_coerce_plan(plan))

        if persist:
            try:
                analysis.claims = result.model_dump(mode="json")
                await session.commit()
            except Exception as exc:  # noqa: BLE001 - persistence is best-effort
                logger.warning("claims_persist_failed task=%s error=%s", analysis.task_id, exc)
                await session.rollback()

        return result

    @staticmethod
    def stored_claims(analysis: Analysis) -> Optional[Dict[str, Any]]:
        """Return the previously persisted claims payload, if any."""
        return getattr(analysis, "claims", None)
