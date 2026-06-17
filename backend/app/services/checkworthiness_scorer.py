"""Checkworthiness scoring for advertising claims (VeritasAd 2.0, M2).

Implements the feature-based checkworthiness model from the master's roadmap
(``docs/research/roadmaps/master-2.0.md`` §10): a continuous score in [0, 1]
expressing how strongly a claim needs external verification.

The scorer is **transparent and fully offline** — it is a weighted sum of
interpretable binary/▒graded features (presence of numbers, comparisons, result
promises, financial/medical/legal context, certifications/guarantees, time
limits, and potential user harm). Returning the per-feature contributions makes
the score explainable in the UI and usable as input features for the supervised
baselines planned in M4.
"""
from __future__ import annotations

import re
from typing import Dict, Tuple

# --- Feature detectors (Russian + English, case-insensitive, substring stems) ---

# Numbers, percentages, money amounts, multipliers ("в 2 раза", "x2").
_NUMBER_RE = re.compile(
    r"(\d+[.,]?\d*\s*%|\d+[.,]?\d*\s*(₽|руб|rub|\$|€|usd|eur)|"
    r"в\s*\d+\s*раз|x\s*\d+|\d{2,}|\d+[.,]\d+)",
    re.IGNORECASE,
)

# Comparative constructs ("быстрее", "дешевле", "чем у конкурентов", "better than").
_COMPARATIVE_RE = re.compile(
    r"(быстрее|дешевле|лучше|выгоднее|эффективнее|надёжнее|надежнее|больше|меньше|"
    r"чем\s+у|по\s+сравнению|конкурент|faster|cheaper|better|more\s+than|compared)",
    re.IGNORECASE,
)

# Result / outcome promises ("гарантируем результат", "похудеете", "заработаете").
_RESULT_PROMISE_RE = re.compile(
    r"(гарант|результат|обещаем|добьёт|добьет|похуде|заработа|избав|вылеч|"
    r"увеличит|снизит|вернём|вернем|guarantee|result|achieve|earn|lose\s+weight)",
    re.IGNORECASE,
)

# Financial / medical / legal context (high-stakes domains).
_FINANCIAL_RE = re.compile(
    r"(кэшбек|кэшбэк|cashback|доход|процент|ставк|кредит|вклад|инвест|"
    r"экономи|выгод|деньг|зарабо|депозит|cashback|income|invest|profit|loan)",
    re.IGNORECASE,
)
_MEDICAL_RE = re.compile(
    r"(здоров|безопасн|лечени|лечит|витамин|клиническ|побочн|болезн|симптом|"
    r"иммунитет|медицин|препарат|health|safe|clinical|cure|medical)",
    re.IGNORECASE,
)
_LEGAL_RE = re.compile(
    r"(сертифиц|сертификат|лицензи|гост|официальн|патент|зарегистрир|"
    r"соответствует\s+требован|certified|licensed|official|patent|registered)",
    re.IGNORECASE,
)

# Certifications, guarantees, official status.
_CERTIFICATION_RE = re.compile(
    r"(сертифиц|гарант|официальн|оригинальн|подлинн|лицензи|проверен|"
    r"одобрен|рекомендуют\s+врач|certified|guarantee|official|authentic|approved)",
    re.IGNORECASE,
)

# Time limits / scarcity ("только сегодня", "успей", "осталось").
_TIME_LIMIT_RE = re.compile(
    r"(только\s+сегодня|только\s+сейчас|успей|ограничен|последн|осталось|"
    r"акция\s+до|до\s+конца|сейчас|сегодня|today\s+only|limited|hurry|last\s+chance)",
    re.IGNORECASE,
)

# Potential user harm if false (health/finance/safety stakes).
_HARM_RE = re.compile(
    r"(здоров|безопасн|детей|ребен|ребён|деньг|кредит|инвест|лечени|"
    r"побочн|вред|риск|гарантированн\w*\s+доход|harm|risk|children|safety)",
    re.IGNORECASE,
)


# Per-feature weights. Tuned so a single number ("скидка 70%") lands in the
# "desirable" band, while a financial/medical promise with numbers reaches the
# "required" band. The raw weighted sum is clamped to [0, 1].
_WEIGHTS: Dict[str, float] = {
    "has_numbers": 0.28,
    "has_comparison": 0.18,
    "has_result_promise": 0.20,
    "has_financial_context": 0.22,
    "has_medical_context": 0.26,
    "has_legal_context": 0.18,
    "has_certification": 0.16,
    "has_time_limit": 0.12,
    "potential_harm": 0.20,
}


def extract_features(text: str) -> Dict[str, float]:
    """Return the binary checkworthiness features for a claim fragment."""
    t = text or ""
    return {
        "has_numbers": 1.0 if _NUMBER_RE.search(t) else 0.0,
        "has_comparison": 1.0 if _COMPARATIVE_RE.search(t) else 0.0,
        "has_result_promise": 1.0 if _RESULT_PROMISE_RE.search(t) else 0.0,
        "has_financial_context": 1.0 if _FINANCIAL_RE.search(t) else 0.0,
        "has_medical_context": 1.0 if _MEDICAL_RE.search(t) else 0.0,
        "has_legal_context": 1.0 if _LEGAL_RE.search(t) else 0.0,
        "has_certification": 1.0 if _CERTIFICATION_RE.search(t) else 0.0,
        "has_time_limit": 1.0 if _TIME_LIMIT_RE.search(t) else 0.0,
        "potential_harm": 1.0 if _HARM_RE.search(t) else 0.0,
    }


def score_checkworthiness(text: str) -> Tuple[float, Dict[str, float]]:
    """Score a claim fragment's checkworthiness.

    Returns:
        A ``(score, features)`` tuple where ``score`` is the clamped weighted sum
        in [0, 1] and ``features`` maps each feature name to its contribution
        (weight × indicator) for explainability.
    """
    features = extract_features(text)
    contributions = {name: features[name] * _WEIGHTS[name] for name in features}
    score = min(1.0, max(0.0, sum(contributions.values())))
    return score, contributions


def is_checkable_from_score(score: float, threshold: float = 0.26) -> bool:
    """Heuristic checkability gate: a fragment with no verifiable signal scores ~0."""
    return score >= threshold
