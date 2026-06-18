"""Claim normalization (VeritasAd 2.0, M2).

Rewrites a raw advertising fragment into a stricter, more verifiable form
(roadmap §7.1 "Claim Normalizer"; annotation guidelines "Нормализация
утверждений").

This module provides the **rule-based** normalizer: a conservative, offline
cleanup that strips scarcity/CTA noise and marketing punctuation while preserving
quantitative bounds (e.g. keeps "до 70%" as an upper bound rather than asserting
"70%"). Full semantic normalization (subject + measurable predicate) is performed
by the LLM extraction methods; the rule-based pass is the deterministic baseline
and the fallback when no LLM is configured.
"""
from __future__ import annotations

import re

# Scarcity / time-limit / CTA clauses that carry no verifiable content and are
# dropped during normalization.
_NOISE_CLAUSE_RE = re.compile(
    r"(только\s+сегодня|только\s+сейчас|успей(те)?\s+купить|успей(те)?|"
    r"переходи(те)?\s+по\s+ссылк\w*|ссылк\w*\s+в\s+описани\w*|по\s+промокод\w*|"
    r"жми|подпиш\w*|закажи(те)?\s+(прямо\s+)?сейчас|не\s+пропусти|"
    r"today\s+only|hurry\s+up|link\s+in\s+(bio|description)|use\s+promo\w*)",
    re.IGNORECASE,
)

# Leading filler ("кстати,", "а ещё", "друзья,") and trailing marketing emphasis.
_LEADING_FILLER_RE = re.compile(
    r"^\s*(кстати|а\s+ещё|а\s+еще|друзья|ребят\w*|так\s+вот|итак)\W+",
    re.IGNORECASE,
)
_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+",
    flags=re.UNICODE,
)
_MULTISPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Return a conservatively normalized, verifiable form of ``text``.

    The transformation is intentionally lossless w.r.t. measurable content: it
    removes scarcity/CTA noise, emoji and filler, then tidies whitespace and
    capitalisation. If the cleanup empties the string, the trimmed raw text is
    returned unchanged.
    """
    if not text:
        return ""

    cleaned = _EMOJI_RE.sub(" ", text)
    cleaned = _NOISE_CLAUSE_RE.sub(" ", cleaned)
    cleaned = _LEADING_FILLER_RE.sub("", cleaned)

    # Drop dangling separators left behind by clause removal.
    cleaned = re.sub(r"[\s,;:—–-]+$", "", cleaned)
    cleaned = re.sub(r"^[\s,;:—–-]+", "", cleaned)
    cleaned = _MULTISPACE_RE.sub(" ", cleaned).strip()

    if not cleaned:
        return _MULTISPACE_RE.sub(" ", text).strip()

    # Capitalise the first character without touching the rest (preserves units
    # like "кВт", brand casing, etc.).
    return cleaned[0].upper() + cleaned[1:]
