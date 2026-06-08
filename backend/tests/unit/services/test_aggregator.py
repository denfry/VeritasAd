"""Tests for temporal NMS aggregation (thesis sec. 3.2)."""
from app.services.aggregator import temporal_iou, nms_temporal, build_ad_segments


def test_temporal_iou_full_overlap():
    a = {"start": 0.0, "end": 10.0}
    assert temporal_iou(a, a) == 1.0


def test_temporal_iou_no_overlap():
    a = {"start": 0.0, "end": 5.0}
    b = {"start": 10.0, "end": 15.0}
    assert temporal_iou(a, b) == 0.0


def test_temporal_iou_partial():
    a = {"start": 0.0, "end": 4.0}
    b = {"start": 2.0, "end": 6.0}
    # intersection = 2, union = 6
    assert abs(temporal_iou(a, b) - (2.0 / 6.0)) < 1e-9


def test_nms_suppresses_lower_score_overlap():
    cands = [
        {"start": 0.0, "end": 4.0, "w_score": 0.9},
        {"start": 1.0, "end": 5.0, "w_score": 0.5},  # IoU>0.5 with the first
    ]
    kept = nms_temporal(cands)
    assert len(kept) == 1
    assert kept[0]["w_score"] == 0.9


def test_nms_keeps_disjoint_segments_sorted():
    cands = [
        {"start": 20.0, "end": 24.0, "w_score": 0.8},
        {"start": 0.0, "end": 4.0, "w_score": 0.9},
    ]
    kept = nms_temporal(cands)
    assert [c["start"] for c in kept] == [0.0, 20.0]


def test_nms_drops_below_score_threshold():
    cands = [{"start": 0.0, "end": 4.0, "w_score": 0.2}]
    assert nms_temporal(cands) == []


def test_build_ad_segments_from_brands():
    brands = [{"name": "Acme", "confidence": 0.7, "timestamps": [0.0, 30.0]}]
    segments = build_ad_segments(brands)
    assert len(segments) == 2
    assert all(seg["brand"] == "Acme" for seg in segments)
    assert all(seg["end"] - seg["start"] == 2.0 for seg in segments)


def test_build_ad_segments_filters_low_confidence():
    brands = [{"name": "Weak", "confidence": 0.1, "timestamps": [5.0]}]
    assert build_ad_segments(brands) == []
