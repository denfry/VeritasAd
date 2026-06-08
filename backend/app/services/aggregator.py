"""Temporal aggregation of advertising candidates.

Implements Non-Maximum Suppression (NMS) over the time axis, as described in the
thesis (sec. 3.2 "Агрегация результатов"): candidate advertising segments are
ranked by their weighted score; overlapping candidates (temporal IoU > 0.5) are
suppressed in favour of the highest-scoring one, and candidates whose weighted
score is below 0.40 are discarded.

In addition to visual (logo) candidates, advertising reads are localised on the
audio transcript: Whisper segments carry ``start``/``end`` timestamps, so the
spoken sponsor integrations ("...переходите по ссылке в описании") can be placed
on the timeline even when no on-screen logo is recognised.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence

# Thresholds per thesis sec. 3.2.
DEFAULT_IOU_THRESHOLD = 0.5
DEFAULT_SCORE_THRESHOLD = 0.40

# Adjacent kept segments closer than this (seconds) are merged into one block so
# the output is a few clean ad intervals instead of many 2-second fragments.
# Sized to bridge a short non-ad filler line in the middle of a sponsor read
# without joining genuinely separate integrations (which sit minutes apart).
DEFAULT_MERGE_GAP_SECONDS = 12.0

# Call-to-action / sponsorship phrases spoken during ad reads, with weights.
# These are strong, ad-specific signals (unlike single product nouns).
_CTA_PATTERNS: List[tuple] = [
    (re.compile(r"по\s+ссылк\w*\s+в\s+описани", re.I), "по ссылке в описании", 0.7),
    (re.compile(r"ссылк\w*\s+в\s+(описани|профил|шапк|коммент)", re.I), "ссылка в описании", 0.6),
    (re.compile(r"перехо\w*\s+по\s+ссылк", re.I), "переходите по ссылке", 0.6),
    (re.compile(r"перехо\w*\s+на\s+сайт", re.I), "переходите на сайт", 0.5),
    (re.compile(r"успе\w*\s+купить", re.I), "успей купить", 0.5),
    (re.compile(r"по\s+промокод", re.I), "по промокоду", 0.6),
    (re.compile(r"промокод\w*", re.I), "промокод", 0.45),
    (re.compile(r"зарегистрир\w+", re.I), "регистрация", 0.4),
    (re.compile(r"скидк\w*\s+\d", re.I), "скидка N%", 0.4),
    (re.compile(r"в\s+описани\w*", re.I), "в описании", 0.35),
]

# Per-signal weights for transcript scoring.
_KEYWORD_WEIGHT = 0.2
_KEYWORD_CAP = 0.5
_BRAND_WEIGHT = 0.35
_BRAND_CAP = 0.6
# A transcript segment qualifies as an ad read at/above this score. Tuned so a
# single generic product noun does NOT trigger (0.2 < 0.34), but a brand
# mention, a CTA phrase, or two co-occurring product terms do.
DEFAULT_TRANSCRIPT_MIN_SCORE = 0.34

# A transcript segment carries an ad "signal" at/above this score (one product
# keyword is enough). Used for density-based localisation of long product demos.
_WEAK_SIGNAL_FLOOR = 0.18
# A run of weak signals becomes an ad block when it has at least this many
# signal segments and their scores sum to at least this much — i.e. a sustained
# cluster, not a one-off mention.
_DENSITY_MIN_SEGMENTS = 3
_DENSITY_MIN_SUM = 0.9


def temporal_iou(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """Intersection-over-Union of two segments on the time axis.

    Each segment is a dict with ``start`` and ``end`` keys (seconds).
    Returns a value in [0, 1]; 0 when the segments do not overlap.
    """
    a_start, a_end = float(a["start"]), float(a["end"])
    b_start, b_end = float(b["start"]), float(b["end"])
    inter = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    return inter / union if union > 0 else 0.0


def nms_temporal(
    candidates: Sequence[Dict[str, Any]],
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Apply temporal Non-Maximum Suppression to candidate ad segments.

    Args:
        candidates: segments, each a dict with ``start``, ``end`` and
            ``w_score`` (weighted confidence) keys.
        iou_threshold: candidates overlapping a kept segment by more than this
            temporal IoU are suppressed.
        score_threshold: candidates with ``w_score`` below this are dropped.

    Returns:
        The kept segments, sorted by ``start`` ascending.
    """
    filtered = [c for c in candidates if float(c.get("w_score", 0.0)) >= score_threshold]
    filtered.sort(key=lambda c: float(c.get("w_score", 0.0)), reverse=True)

    kept: List[Dict[str, Any]] = []
    for cand in filtered:
        if not any(temporal_iou(cand, k) > iou_threshold for k in kept):
            kept.append(cand)

    return sorted(kept, key=lambda c: float(c["start"]))


def _word_regex(term: str) -> "re.Pattern[str]":
    """Whole-token, case-insensitive matcher for a brand/alias term."""
    return re.compile(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", re.I)


def localize_transcript_ads(
    transcript_segments: Sequence[Dict[str, Any]] | None,
    ad_keywords: Sequence[str] | None = None,
    brand_terms: Sequence[str] | None = None,
    *,
    min_score: float = DEFAULT_TRANSCRIPT_MIN_SCORE,
    merge_gap: float = DEFAULT_MERGE_GAP_SECONDS,
) -> List[Dict[str, Any]]:
    """Localise spoken advertising reads on the audio transcript timeline.

    Each Whisper segment (``{start, end, text}``) is scored by the presence of
    CTA phrases, advertising keywords and known brand mentions. Segments scoring
    at/above ``min_score`` are treated as ad reads and consecutive ones (gap
    ``<= merge_gap``) are merged into contiguous blocks.

    Returns a list of ``{start, end, w_score, brand, source, evidence}`` blocks.
    """
    segments = transcript_segments or []
    if not segments:
        return []

    keywords = [k.lower() for k in (ad_keywords or []) if k]
    brands = sorted(
        {b.lower() for b in (brand_terms or []) if b and len(b) >= 3},
        key=len,
        reverse=True,
    )
    brand_patterns = [(b, _word_regex(b)) for b in brands]

    scored: List[Dict[str, Any]] = []
    for seg in segments:
        text = str(seg.get("text") or "").strip()
        if not text:
            continue
        low = text.lower()

        score = 0.0
        evidence: List[str] = []

        for pattern, label, weight in _CTA_PATTERNS:
            if pattern.search(low):
                score += weight
                evidence.append(label)

        kw_hits = [k for k in keywords if k in low]
        if kw_hits:
            score += min(_KEYWORD_CAP, _KEYWORD_WEIGHT * len(kw_hits))
            evidence.extend(kw_hits[:4])

        # Brand mentions only count as a *booster* on top of a CTA/keyword
        # signal — never as a sole trigger. Many Russian brand names are common
        # words ("Победа", "Лента", "Магнит") and would false-fire on ordinary
        # speech if allowed to localise an ad on their own.
        if score > 0:
            brand_hits = [name for name, pat in brand_patterns if pat.search(low)]
            if brand_hits:
                score += min(_BRAND_CAP, _BRAND_WEIGHT * len(brand_hits))
                evidence.extend(brand_hits[:3])

        if score <= 0:
            continue
        try:
            start = float(seg["start"])
            end = float(seg["end"])
        except (KeyError, TypeError, ValueError):
            continue
        scored.append(
            {
                "start": start,
                "end": end,
                "raw": min(1.0, score),
                "evidence": list(dict.fromkeys(evidence)),
            }
        )

    if not scored:
        return []
    scored.sort(key=lambda s: s["start"])

    # Group consecutive signal-bearing segments (gap <= merge_gap) into runs,
    # then accept a run as an ad block when it is either anchored by a strong
    # segment (a CTA phrase, two product keywords, or keyword+brand) OR carries
    # a *dense* cluster of weak signals. Density matters because Whisper often
    # mishears brand names ("Redmi" -> "Red Minute") and a product demo is split
    # into many short lines each holding a single keyword — individually below
    # threshold, but collectively an unmistakable ad read. An isolated weak hit
    # (e.g. one "наушники" line in ordinary footage) never reaches the density
    # bar, so this does not cost precision.
    runs: List[Dict[str, Any]] = []
    for seg in scored:
        if seg["raw"] < _WEAK_SIGNAL_FLOOR:
            continue
        if runs and seg["start"] - runs[-1]["end"] <= merge_gap:
            run = runs[-1]
            run["end"] = max(run["end"], seg["end"])
            run["segs"].append(seg)
        else:
            runs.append({"start": seg["start"], "end": seg["end"], "segs": [seg]})

    blocks: List[Dict[str, Any]] = []
    for run in runs:
        segs = run["segs"]
        max_raw = max(s["raw"] for s in segs)
        raw_sum = sum(s["raw"] for s in segs)
        has_strong = max_raw >= min_score
        is_dense = len(segs) >= _DENSITY_MIN_SEGMENTS and raw_sum >= _DENSITY_MIN_SUM
        if not (has_strong or is_dense):
            continue

        if has_strong:
            w_score = min(1.0, max_raw)
        else:
            # Density-only block: confidence grows with the number of weak hits.
            w_score = min(1.0, 0.5 + 0.08 * (len(segs) - _DENSITY_MIN_SEGMENTS))

        evidence: List[str] = []
        for s in segs:
            evidence.extend(s["evidence"])
        blocks.append(
            {
                "start": run["start"],
                "end": run["end"],
                "w_score": w_score,
                "brand": "",
                "source": "transcript",
                "evidence": list(dict.fromkeys(evidence)),
            }
        )
    return blocks


def _merge_adjacent(
    segments: Sequence[Dict[str, Any]],
    merge_gap: float = DEFAULT_MERGE_GAP_SECONDS,
) -> List[Dict[str, Any]]:
    """Merge kept segments closer than ``merge_gap`` seconds into single blocks."""
    if not segments:
        return []
    ordered = sorted(segments, key=lambda s: float(s["start"]))
    merged: List[Dict[str, Any]] = [dict(ordered[0])]
    for seg in ordered[1:]:
        last = merged[-1]
        if float(seg["start"]) - float(last["end"]) <= merge_gap:
            last["end"] = max(float(last["end"]), float(seg["end"]))
            last["w_score"] = max(float(last["w_score"]), float(seg.get("w_score", 0.0)))
            names = [n for n in [last.get("brand"), seg.get("brand")] if n]
            last["brand"] = ", ".join(dict.fromkeys(names))
            srcs = [s for s in [last.get("source"), seg.get("source")] if s]
            last["source"] = ",".join(dict.fromkeys(",".join(srcs).split(",")))
            ev = (last.get("evidence") or []) + (seg.get("evidence") or [])
            if ev:
                last["evidence"] = list(dict.fromkeys(ev))
        else:
            merged.append(dict(seg))
    return merged


def build_ad_segments(
    detected_brands: Sequence[Dict[str, Any]] | None,
    transcript_segments: Sequence[Dict[str, Any]] | None = None,
    *,
    ad_keywords: Sequence[str] | None = None,
    brand_terms: Sequence[str] | None = None,
    window_seconds: float = 2.0,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    merge_gap: float = DEFAULT_MERGE_GAP_SECONDS,
) -> List[Dict[str, Any]]:
    """Build candidate advertising segments and collapse them into ad blocks.

    Two evidence sources are combined:

    * **Visual** — each recognised brand timestamp opens a window
      ``[t, t + window_seconds]`` weighted by the brand confidence. Brands with
      no timestamps (text-only mentions) and low-confidence ``Unknown``/fallback
      detections are ignored — the latter caused false segments on ad-free
      footage.
    * **Transcript** — spoken sponsor reads localised via
      :func:`localize_transcript_ads`.

    Overlapping candidates are suppressed with :func:`nms_temporal`; the survivors
    are then merged into contiguous blocks (:func:`_merge_adjacent`).
    """
    candidates: List[Dict[str, Any]] = []

    for brand in detected_brands or []:
        source = str(brand.get("source", "")).lower()
        # Skip non-identifying visual signals: low-confidence ``fallback``/
        # ``Unknown`` hits and generic ``zero_shot`` "company logo" matches. They
        # indicate "maybe a logo" but not which brand, and placing them on the
        # timeline produced false ad segments on logo-free footage.
        if brand.get("is_unknown") or "fallback" in source or "zero_shot" in source:
            continue
        confidence = float(brand.get("confidence", 0.0))
        name = str(brand.get("name", "")).strip()
        for ts in brand.get("timestamps", []) or []:
            try:
                start = float(ts)
            except (TypeError, ValueError):
                continue
            candidates.append(
                {
                    "start": start,
                    "end": start + window_seconds,
                    "w_score": confidence,
                    "brand": name,
                    "source": "visual",
                }
            )

    candidates.extend(
        localize_transcript_ads(
            transcript_segments,
            ad_keywords=ad_keywords,
            brand_terms=brand_terms,
            merge_gap=merge_gap,
        )
    )

    kept = nms_temporal(
        candidates,
        iou_threshold=iou_threshold,
        score_threshold=score_threshold,
    )
    return _merge_adjacent(kept, merge_gap=merge_gap)
