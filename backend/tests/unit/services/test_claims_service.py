"""Tests for the claims domain service (VeritasAd 2.0, M2).

``request_from_analysis`` is exercised against a lightweight ``SimpleNamespace``
stub (no DB / ORM), and ``extract`` is run offline with ``MOCK_LLM_RESPONSES``.
"""
import os
from types import SimpleNamespace

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["MOCK_LLM_RESPONSES"] = "true"

from app.domains.claims.service import ClaimsService  # noqa: E402
from app.schemas.claims import (  # noqa: E402
    ClaimExtractionRequest,
    ClaimExtractionResult,
    ExtractionMethod,
)


def _stub_analysis() -> SimpleNamespace:
    return SimpleNamespace(
        transcript="Скидка до 70% только сегодня. Кэшбек 16% годовых.",
        detected_brands=[{"name": "Acme", "confidence": 0.9}],
        disclosure_markers=["#ad"],
        cta_matches=["жми"],
        commercial_urls=["https://track.example/x"],
        video_id="vid-42",
        source_type="video",
        source_url="https://example.com/v",
    )


def test_request_from_analysis_builds_request_from_stub():
    request = ClaimsService.request_from_analysis(
        _stub_analysis(), ExtractionMethod.RULE_BASED
    )

    assert isinstance(request, ClaimExtractionRequest)
    assert request.method == ExtractionMethod.RULE_BASED
    assert request.content_id == "vid-42"
    assert request.source_type == "video"
    assert request.source_url == "https://example.com/v"
    assert request.transcript == "Скидка до 70% только сегодня. Кэшбек 16% годовых."
    assert request.detected_brands == [{"name": "Acme", "confidence": 0.9}]
    assert request.disclosure_markers == ["#ad"]
    assert request.cta_matches == ["жми"]
    assert request.commercial_urls == ["https://track.example/x"]


def test_request_from_analysis_handles_empty_optional_signals():
    stub = SimpleNamespace(
        transcript=None,
        detected_brands=None,
        disclosure_markers=None,
        video_id="vid-x",
        source_type="post",
        source_url=None,
        # cta_matches / commercial_urls intentionally absent (getattr fallback).
    )
    request = ClaimsService.request_from_analysis(stub, ExtractionMethod.RULE_BASED)
    assert request.transcript == ""
    assert request.detected_brands == []
    assert request.disclosure_markers == []
    assert request.cta_matches == []
    assert request.commercial_urls == []
    assert request.content_id == "vid-x"
    assert request.source_type == "post"


async def test_extract_returns_extraction_result():
    service = ClaimsService()
    request = ClaimsService.request_from_analysis(
        _stub_analysis(), ExtractionMethod.RULE_BASED
    )
    result = await service.extract(request)

    assert isinstance(result, ClaimExtractionResult)
    assert result.method == ExtractionMethod.RULE_BASED
    assert result.content_id == "vid-42"
    assert len(result.claims) >= 1
