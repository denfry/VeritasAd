from __future__ import annotations

import re

from .schema import DisclosureMatch, MarkerType

_ERID_RE = re.compile(r"erid\s*[:=]\s*([A-Za-z0-9]{6,})", re.IGNORECASE)
_INN_RE = re.compile(
    r"рекламодател[ья][^\n]{0,60}?\bИНН\b\s*[:№]?\s*([0-9]{10,12})",
    re.IGNORECASE,
)
_HASHTAG_RE = re.compile(r"#(?:реклама|ad|sponsored|спонсор)\b", re.IGNORECASE)
_PHRASE_AD_RE = re.compile(
    r"на\s+правах\s+рекламы|рекламн\w*\s+интеграци\w*|партн[её]рск\w*\s+материал\w*",
    re.IGNORECASE,
)
_SPONSOR_RE = re.compile(
    r"при\s+поддержк\w+|спонсор\w*\s+(?:этого\s+)?(?:выпуск\w+|ролик\w+|видео)",
    re.IGNORECASE,
)
_PROMO_RE = re.compile(r"промокод\w*\s+([A-Za-z0-9]{3,})", re.IGNORECASE)


def mine_disclosure(text: str) -> list[DisclosureMatch]:
    """Extract advertising-disclosure markers from a text surface.

    Order is fixed (strong markers first) so output is deterministic.
    """
    matches: list[DisclosureMatch] = []
    if not text:
        return matches
    for m in _ERID_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.ERID, m.group(0), value=m.group(1)))
    for m in _INN_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.ADVERTISER_INN, m.group(0), value=m.group(1)))
    for m in _HASHTAG_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.HASHTAG_AD, m.group(0)))
    for m in _PHRASE_AD_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.PHRASE_AD, m.group(0)))
    for m in _SPONSOR_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.SPONSOR_PHRASE, m.group(0)))
    for m in _PROMO_RE.finditer(text):
        matches.append(DisclosureMatch(MarkerType.PROMO_CODE, m.group(0), value=m.group(1)))
    return matches
