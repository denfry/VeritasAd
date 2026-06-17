"""Tests for the offline checkworthiness scorer (VeritasAd 2.0, M2 roadmap §10)."""
from app.services.checkworthiness_scorer import (
    extract_features,
    is_checkable_from_score,
    score_checkworthiness,
)


def test_features_present_for_numbers():
    features = extract_features("скидка до 70% на всё")
    assert features["has_numbers"] == 1.0


def test_features_present_for_financial():
    features = extract_features("кэшбек 16% годовых на остаток")
    assert features["has_financial_context"] == 1.0


def test_features_present_for_medical():
    features = extract_features("клинически доказанная польза для здоровья")
    assert features["has_medical_context"] == 1.0


def test_features_present_for_time_limit():
    features = extract_features("успей купить только сегодня")
    assert features["has_time_limit"] == 1.0


def test_score_in_unit_interval():
    score, contributions = score_checkworthiness(
        "кэшбек 16% годовых, гарантированный доход для здоровья ваших детей"
    )
    assert 0.0 <= score <= 1.0
    # Every contribution is weight * indicator, never negative.
    assert all(value >= 0.0 for value in contributions.values())


def test_empty_text_scores_zero():
    score, contributions = score_checkworthiness("")
    assert score == 0.0
    assert all(value == 0.0 for value in contributions.values())


def test_none_text_scores_zero():
    score, _ = score_checkworthiness(None)  # type: ignore[arg-type]
    assert score == 0.0


def test_financial_medical_scores_higher_than_bare_subjective():
    high, _ = score_checkworthiness(
        "кэшбек 16% годовых, полезно для здоровья и безопасно для детей"
    )
    low, _ = score_checkworthiness("это прекрасный выбор")
    assert high > low


def test_contributions_sum_to_score():
    score, contributions = score_checkworthiness("скидка до 70%")
    assert abs(sum(contributions.values()) - score) < 1e-9


def test_is_checkable_gate():
    # A bare subjective phrase scores ~0 and is below the checkability threshold.
    assert is_checkable_from_score(0.0) is False
    # A financial number-bearing fragment clears the gate.
    score, _ = score_checkworthiness("кэшбек 16% годовых")
    assert is_checkable_from_score(score) is True
