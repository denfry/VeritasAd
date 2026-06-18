"""Tests for the rule-based claim classifier (VeritasAd 2.0, M2 roadmap §8/§9)."""
from app.schemas.claims import ClaimType, RiskLevel
from app.services.claim_classifier import (
    assess_risk,
    classify,
    classify_type,
    coerce_claim_type,
    coerce_risk_level,
)


def test_discount_is_measurable_type():
    # A bare percentage discount is measurable (quantitative); when wrapped in
    # scarcity ("только сегодня") the availability detector wins first.
    assert classify_type("скидка до 70%") in (
        ClaimType.QUANTITATIVE,
        ClaimType.AVAILABILITY,
    )


def test_delivery_time_is_temporal():
    assert classify_type("доставка за 24 часа") == ClaimType.TEMPORAL


def test_cashback_is_financial():
    assert classify_type("кэшбек 16% годовых") == ClaimType.FINANCIAL


def test_gost_certification_is_legal():
    assert classify_type("сертифицировано по ГОСТ") == ClaimType.LEGAL_CERTIFICATION


def test_official_partner_is_partnership():
    assert classify_type("официальный партнёр чемпионата") == ClaimType.PARTNERSHIP


def test_best_service_is_superlative():
    assert classify_type("лучший сервис") == ClaimType.SUPERLATIVE


def test_you_will_like_it_is_not_checkable():
    assert classify_type("вам понравится") in (
        ClaimType.SUBJECTIVE,
        ClaimType.NON_CHECKABLE,
    )


def test_assess_risk_financial_is_high():
    assert assess_risk("кэшбек 16% годовых", ClaimType.FINANCIAL) == RiskLevel.HIGH


def test_assess_risk_health_is_high():
    assert (
        assess_risk("безопасно для взрослых", ClaimType.HEALTH_SAFETY) == RiskLevel.HIGH
    )


def test_assess_risk_legal_is_high():
    assert (
        assess_risk("соответствует стандарту", ClaimType.LEGAL_CERTIFICATION)
        == RiskLevel.HIGH
    )


def test_assess_risk_critical_wording_escalates():
    # Harm wording ("для детей") escalates above the base type risk.
    assert assess_risk("безопасно для детей", ClaimType.HEALTH_SAFETY) == RiskLevel.CRITICAL


def test_assess_risk_subjective_is_low():
    assert assess_risk("прекрасный выбор", ClaimType.SUBJECTIVE) == RiskLevel.LOW


def test_classify_returns_type_and_risk():
    claim_type, risk = classify("кэшбек 16% годовых")
    assert claim_type == ClaimType.FINANCIAL
    assert risk == RiskLevel.HIGH


def test_coerce_claim_type_snaps_valid_string():
    assert coerce_claim_type("financial") == ClaimType.FINANCIAL
    assert coerce_claim_type("health-safety") == ClaimType.HEALTH_SAFETY
    assert coerce_claim_type("LEGAL CERTIFICATION") == ClaimType.LEGAL_CERTIFICATION


def test_coerce_claim_type_falls_back_on_garbage():
    # Unknown value -> rule-based classification of the fallback text.
    assert coerce_claim_type("???not-a-type", fallback_text="доставка за 24 часа") == (
        ClaimType.TEMPORAL
    )
    assert coerce_claim_type(None, fallback_text="лучший сервис") == ClaimType.SUPERLATIVE


def test_coerce_risk_level_snaps_valid_string():
    assert coerce_risk_level("critical", ClaimType.FINANCIAL) == RiskLevel.CRITICAL
    assert coerce_risk_level("LOW", ClaimType.SUBJECTIVE) == RiskLevel.LOW


def test_coerce_risk_level_falls_back_on_garbage():
    # Unknown value -> assess_risk from the claim type / fallback text.
    assert coerce_risk_level("???", ClaimType.FINANCIAL) == RiskLevel.HIGH
    assert coerce_risk_level(None, ClaimType.SUBJECTIVE) == RiskLevel.LOW
