"""Tests for the claim-extraction orchestrator (VeritasAd 2.0, M2 roadmap §7.2).

The LLM extraction path is exercised offline via ``MOCK_LLM_RESPONSES``; the env
flags are set at import top, before any ``app`` module is imported, alongside the
``DATABASE_URL`` the conftest also sets.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["MOCK_LLM_RESPONSES"] = "true"

from app.schemas.claims import (  # noqa: E402
    ClaimExtractionRequest,
    ClaimExtractionResult,
    ExtractionMethod,
)
from app.services.claim_extractor import ClaimExtractor  # noqa: E402


def _multimodal_request() -> ClaimExtractionRequest:
    return ClaimExtractionRequest(
        transcript=(
            "Скидка до 70% только сегодня. "
            "Кэшбек 16% годовых на остаток. "
            "Вам точно понравится."
        ),
        ocr_text="Сертифицировано по ГОСТ. Доставка за 24 часа.",
        method=ExtractionMethod.RULE_BASED,
        content_id="vid-1",
        source_type="video",
        source_url="https://example.com/v",
    )


async def test_rule_based_yields_sorted_claims_with_stable_ids():
    extractor = ClaimExtractor()
    result = await extractor.extract(_multimodal_request())

    assert isinstance(result, ClaimExtractionResult)
    assert result.method == ExtractionMethod.RULE_BASED
    assert result.model is None
    assert len(result.claims) >= 1

    # Ids are claim_001, claim_002, ... in order.
    expected_ids = [f"claim_{i:03d}" for i in range(1, len(result.claims) + 1)]
    assert [c.id for c in result.claims] == expected_ids

    # Sorted by checkworthiness descending.
    scores = [c.checkworthiness_score for c in result.claims]
    assert scores == sorted(scores, reverse=True)


async def test_rule_based_surfaces_measurable_fragments():
    extractor = ClaimExtractor()
    result = await extractor.extract(_multimodal_request())

    types = {c.claim_type.value for c in result.claims}
    # Financial, temporal and legal/certification fragments must surface.
    assert "financial" in types
    assert "temporal" in types
    assert "legal_certification" in types


async def test_ad_free_plain_speech_yields_zero_claims():
    extractor = ClaimExtractor()
    request = ClaimExtractionRequest(
        transcript="Сегодня хорошая погода и я гулял в парке",
        method=ExtractionMethod.RULE_BASED,
    )
    result = await extractor.extract(request)
    assert result.claims == []
    assert result.total_claims == 0


async def test_stats_totals_are_consistent():
    extractor = ClaimExtractor()
    result = await extractor.extract(_multimodal_request())

    stats = result.stats
    n = len(result.claims)
    assert stats["total"] == n
    assert stats["checkable"] + stats["non_checkable"] == n
    assert sum(stats["by_type"].values()) == n
    assert sum(stats["by_risk"].values()) == n
    assert 0.0 <= stats["mean_checkworthiness"] <= 1.0


async def test_llm_zero_shot_returns_mock_claims():
    extractor = ClaimExtractor()
    request = ClaimExtractionRequest(
        transcript="Скидка до 70%, вам понравится",
        method=ExtractionMethod.LLM_ZERO_SHOT,
    )
    result = await extractor.extract(request)

    # Method is preserved and a model is reported for the LLM path.
    assert result.method == ExtractionMethod.LLM_ZERO_SHOT
    assert result.model is not None
    # The mock returns two claims: a checkable quantitative one + a non-checkable one.
    assert len(result.claims) == 2
    assert any(c.is_checkable for c in result.claims)
    assert any(not c.is_checkable for c in result.claims)


async def test_llm_few_shot_returns_mock_claims_with_model():
    extractor = ClaimExtractor()
    request = ClaimExtractionRequest(
        transcript="Кэшбек 16% годовых",
        method=ExtractionMethod.LLM_FEW_SHOT,
    )
    result = await extractor.extract(request)
    assert result.method == ExtractionMethod.LLM_FEW_SHOT
    assert result.model is not None
    assert len(result.claims) >= 1
