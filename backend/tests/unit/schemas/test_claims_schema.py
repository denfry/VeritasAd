"""Tests for the claim Pydantic schemas (VeritasAd 2.0, M2 data contract)."""
import pytest
from pydantic import ValidationError

from app.schemas.claims import (
    Claim,
    ClaimExtractionResult,
    checkworthiness_bucket,
)


def _claim(score: float) -> Claim:
    return Claim(id="claim_001", raw_text="x", checkworthiness_score=score)


def test_bucket_boundaries():
    # Boundaries are inclusive-upper: <=0.25 almost_none, <=0.5 low, <=0.75 desirable.
    assert _claim(0.25).checkworthiness_bucket == "almost_none"
    assert _claim(0.5).checkworthiness_bucket == "low"
    assert _claim(0.75).checkworthiness_bucket == "desirable"
    assert _claim(0.9).checkworthiness_bucket == "required"


def test_bucket_helper_matches_property():
    for score in (0.0, 0.25, 0.26, 0.5, 0.51, 0.75, 0.76, 1.0):
        assert _claim(score).checkworthiness_bucket == checkworthiness_bucket(score)


def test_in_range_score_accepted():
    assert _claim(0.0).checkworthiness_score == 0.0
    assert _claim(1.0).checkworthiness_score == 1.0


def test_out_of_range_score_rejected():
    # The field is constrained to [0, 1]; out-of-range values raise.
    with pytest.raises(ValidationError):
        _claim(2.0)
    with pytest.raises(ValidationError):
        _claim(-1.0)


def test_total_claims_counts_claims():
    result = ClaimExtractionResult(claims=[_claim(0.5), _claim(0.3)])
    assert result.total_claims == 2
    assert ClaimExtractionResult().total_claims == 0


def test_claim_defaults():
    claim = Claim(id="claim_001", raw_text="raw")
    assert claim.normalized_claim == ""
    assert claim.is_checkable is False
    assert claim.checkworthiness_score == 0.0
    assert claim.checkworthiness_bucket == "almost_none"
    assert claim.features == {}
