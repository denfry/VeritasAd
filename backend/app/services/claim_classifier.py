"""Advertising claim classification (VeritasAd 2.0, M2).

Assigns a :class:`~app.schemas.claims.ClaimType` (taxonomy, roadmap §8) and a
:class:`~app.schemas.claims.RiskLevel` (roadmap §9) to a claim fragment.

The classifier is rule-based (ordered regex detectors over Russian + English
text) so it works fully offline and gives a deterministic baseline for the M4
experiments. It also exposes :func:`coerce_claim_type` / :func:`coerce_risk_level`
so the LLM extraction methods can validate and snap free-form model output onto
the canonical enums, falling back to the rule-based label when the model returns
something unknown.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

from app.schemas.claims import ClaimType, RiskLevel

# --- Type detectors, evaluated in priority order (first match wins) ---

_SUPERLATIVE_RE = re.compile(
    r"(лучш\w*|самый|№\s*1|номер\s+один|#1|идеальн\w*|непревзойд|"
    r"best|number\s+one|the\s+most|top\s+\d)",
    re.IGNORECASE,
)
_COMPARATIVE_RE = re.compile(
    r"(быстрее|дешевле|выгоднее|эффективнее|надёжнее|надежнее|лучше,?\s+чем|"
    r"чем\s+у\s+конкурент|по\s+сравнению|faster|cheaper|better\s+than|more\s+than)",
    re.IGNORECASE,
)
_LEGAL_RE = re.compile(
    r"(сертифиц|сертификат|лицензи|гост\b|патент|зарегистрир|соответствует\s+требован|"
    r"certified|licensed|patent|registered|iso\s*\d)",
    re.IGNORECASE,
)
_PARTNERSHIP_RE = re.compile(
    r"(официальн\w*\s+(партн|представ|дистриб|магазин|дилер)|официальный\s+партнёр|"
    r"официальный\s+партнер|эксклюзивн\w*\s+партн|official\s+partner|authorized)",
    re.IGNORECASE,
)
_HEALTH_RE = re.compile(
    r"(здоров|безопасн\w*\s+для|гипоаллерген|без\s+вреда|клиническ|витамин|"
    r"иммунитет|для\s+детей|побочн|safe\s+for|clinical|health|hypoallergen)",
    re.IGNORECASE,
)
_FINANCIAL_RE = re.compile(
    r"(кэшбек|кэшбэк|cashback|экономи\w*\s+\d|доход\w*\s+\d|\d+\s*%\s*годовых|"
    r"ставк\w*\s+\d|вернём\s+\d|вернем\s+\d|saving|income|cashback|\d+\s*%\s*apr)",
    re.IGNORECASE,
)
_TEMPORAL_RE = re.compile(
    r"(за\s+\d+\s*(час|минут|дн|day|hour|min)|доставка\s+за|в\s+течени\w*\s+\d|"
    r"\d+\s*(час|минут|дней|дня)\b|within\s+\d+\s*(hour|day|min))",
    re.IGNORECASE,
)
_AVAILABILITY_RE = re.compile(
    r"(только\s+сегодня|только\s+сейчас|успей|ограничен\w*\s+(тираж|количеств|предложен)|"
    r"последн\w*\s+(шанс|штук|экземпляр)|осталось\s+\d|в\s+наличии|распродажа|"
    r"today\s+only|limited|while\s+stocks|last\s+chance)",
    re.IGNORECASE,
)
# Numbers / percentages / measurable amounts (checked after the more specific
# financial/temporal detectors so "доставка за 24 часа" stays temporal).
_QUANTITATIVE_RE = re.compile(
    r"(\d+[.,]?\d*\s*%|скидк\w*\s+(до\s+)?\d|\d+[.,]?\d*\s*(₽|руб|rub|\$|€)|"
    r"в\s*\d+\s*раз|x\s*\d+|\d+[.,]\d+|\bдо\s+\d+)",
    re.IGNORECASE,
)
# Subjective / opinion language.
_SUBJECTIVE_RE = re.compile(
    r"(идеальн|прекрасн|восхитительн|удивительн|потрясающ|невероятн|"
    r"вам\s+понравится|тебе\s+понравится|нравится|любим|amazing|wonderful|perfect|"
    r"you\s*'?ll\s+love|great\s+choice)",
    re.IGNORECASE,
)

# A fragment with none of the above measurable signals and only vague wording is
# treated as non-checkable.
_NON_CHECKABLE_HINT_RE = re.compile(
    r"(тебе\s+понравится|вам\s+понравится|почувствуй|ощути|настроени|"
    r"стиль\s+жизни|you\s*'?ll\s+love|feel\s+the)",
    re.IGNORECASE,
)


def classify_type(text: str) -> ClaimType:
    """Classify a claim fragment into the advertising taxonomy (rule-based)."""
    t = text or ""
    # Order matters: specific high-stakes / structural classes first, generic
    # quantitative next, subjective/non-checkable last.
    if _SUPERLATIVE_RE.search(t):
        return ClaimType.SUPERLATIVE
    if _PARTNERSHIP_RE.search(t):
        return ClaimType.PARTNERSHIP
    if _LEGAL_RE.search(t):
        return ClaimType.LEGAL_CERTIFICATION
    if _HEALTH_RE.search(t):
        return ClaimType.HEALTH_SAFETY
    if _FINANCIAL_RE.search(t):
        return ClaimType.FINANCIAL
    if _TEMPORAL_RE.search(t):
        return ClaimType.TEMPORAL
    if _COMPARATIVE_RE.search(t):
        return ClaimType.COMPARATIVE
    if _AVAILABILITY_RE.search(t):
        return ClaimType.AVAILABILITY
    if _QUANTITATIVE_RE.search(t):
        return ClaimType.QUANTITATIVE
    if _NON_CHECKABLE_HINT_RE.search(t):
        return ClaimType.NON_CHECKABLE
    if _SUBJECTIVE_RE.search(t):
        return ClaimType.SUBJECTIVE
    return ClaimType.SUBJECTIVE


# Claim types that are inherently not externally verifiable.
NON_CHECKABLE_TYPES = frozenset({ClaimType.SUBJECTIVE, ClaimType.NON_CHECKABLE})

# Base risk by claim type (roadmap §9).
_HIGH_RISK_TYPES = frozenset(
    {
        ClaimType.FINANCIAL,
        ClaimType.HEALTH_SAFETY,
        ClaimType.LEGAL_CERTIFICATION,
    }
)
_MEDIUM_RISK_TYPES = frozenset(
    {
        ClaimType.QUANTITATIVE,
        ClaimType.COMPARATIVE,
        ClaimType.SUPERLATIVE,
        ClaimType.TEMPORAL,
        ClaimType.PARTNERSHIP,
        ClaimType.AVAILABILITY,
    }
)

# Regulatory / harm escalation to "critical".
_CRITICAL_RE = re.compile(
    r"(для\s+детей|ребен|ребён|гарантированн\w*\s+доход|без\s+риска|"
    r"100\s*%\s*(результат|эффект|гаранти)|вылеч\w*\s+(от|рак|диабет)|"
    r"похуде\w*\s+на\s+\d|children|guaranteed\s+income|cure\s+(cancer|diabetes))",
    re.IGNORECASE,
)


def assess_risk(text: str, claim_type: ClaimType) -> RiskLevel:
    """Assign a risk level from the claim type and high-stakes wording (roadmap §9)."""
    t = text or ""
    if _CRITICAL_RE.search(t):
        return RiskLevel.CRITICAL
    if claim_type in _HIGH_RISK_TYPES:
        return RiskLevel.HIGH
    if claim_type in NON_CHECKABLE_TYPES:
        return RiskLevel.LOW
    if claim_type in _MEDIUM_RISK_TYPES:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def classify(text: str) -> Tuple[ClaimType, RiskLevel]:
    """Return ``(claim_type, risk_level)`` for a claim fragment (rule-based)."""
    claim_type = classify_type(text)
    return claim_type, assess_risk(text, claim_type)


def coerce_claim_type(value: Optional[str], fallback_text: str = "") -> ClaimType:
    """Snap a free-form (e.g. LLM) claim-type string onto the canonical enum.

    Falls back to rule-based classification of ``fallback_text`` when the value is
    missing or not a recognised member.
    """
    if value:
        normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        for member in ClaimType:
            if normalized == member.value:
                return member
    return classify_type(fallback_text)


def coerce_risk_level(
    value: Optional[str], claim_type: ClaimType, fallback_text: str = ""
) -> RiskLevel:
    """Snap a free-form (e.g. LLM) risk string onto the canonical enum."""
    if value:
        normalized = str(value).strip().lower()
        for member in RiskLevel:
            if normalized == member.value:
                return member
    return assess_risk(fallback_text, claim_type)
