from __future__ import annotations

from .erid_miner import mine_disclosure
from .schema import (
    MarkerType,
    STRONG_MARKERS,
    VideoRecord,
    WeakLabel,
    WeakLabelClass,
    WEAK_MARKERS,
)

_STRENGTH = {
    MarkerType.ERID: 1.0,
    MarkerType.ADVERTISER_INN: 0.95,
    MarkerType.HASHTAG_AD: 0.8,
    MarkerType.PHRASE_AD: 0.75,
}


def build_weak_label(record: VideoRecord) -> WeakLabel:
    """Turn a VideoRecord into a weak label via disclosure mining.

    Only STRONG markers promote a video to the positive (disclosed_ad) set,
    keeping the distant-supervision positives clean. Weak-only signals leave
    the video UNLABELED but flag it for later candidate analysis.
    """
    markers = mine_disclosure(record.disclosure_text())
    has_strong = any(m.marker_type in STRONG_MARKERS for m in markers)
    has_weak = any(m.marker_type in WEAK_MARKERS for m in markers)
    if has_strong:
        confidence = max(_STRENGTH.get(m.marker_type, 0.0) for m in markers)
        return WeakLabel(
            video_id=record.video_id,
            label=WeakLabelClass.DISCLOSED_AD,
            markers=markers,
            confidence=confidence,
            has_weak_signal=has_weak,
        )
    return WeakLabel(
        video_id=record.video_id,
        label=WeakLabelClass.UNLABELED,
        markers=markers,
        confidence=0.0,
        has_weak_signal=has_weak,
    )
