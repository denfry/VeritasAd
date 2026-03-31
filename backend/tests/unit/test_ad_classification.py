from app.utils.ad_classification import (
    classify_advertising,
    compute_analysis_decision,
    compute_brand_signal_score,
    merge_brand_detections,
)


def test_merge_brand_detections_combines_sources_and_counts():
    merged = merge_brand_detections(
        [{"name": "Nike", "confidence": 0.62, "timestamps": [1.0], "source": "known", "frame_count": 1}],
        [{"name": "Nike", "confidence": 0.88, "source": "text_content", "occurrences": 2}],
    )

    assert len(merged) == 1
    assert merged[0]["name"] == "Nike"
    assert merged[0]["confidence"] == 0.88
    assert merged[0]["detections"] >= 3
    assert "text_content" in merged[0]["source"]


def test_compute_brand_signal_score_rewards_repeated_evidence():
    weak = compute_brand_signal_score(
        [{"name": "Brand", "confidence": 0.48, "source": "known", "detections": 1, "total_exposure_seconds": 0.0}]
    )
    strong = compute_brand_signal_score(
        [
            {
                "name": "Brand",
                "confidence": 0.58,
                "source": "known,ocr",
                "detections": 4,
                "total_exposure_seconds": 5.0,
            }
        ]
    )

    assert strong > weak
    assert strong > 0.6


def test_compute_analysis_decision_requires_more_than_single_weak_signal():
    decision = compute_analysis_decision(
        visual_score=0.22,
        audio_score=0.18,
        disclosure_score=0.0,
        link_score=0.0,
        detected_brands=[{"name": "Test", "confidence": 0.42, "source": "known", "detections": 1}],
        disclosure_markers=[],
        detected_keywords=[],
        has_cta=False,
        has_commercial_links=False,
    )

    assert decision["has_advertising"] is False


def test_compute_analysis_decision_flags_hidden_ad_with_multiple_signals():
    decision = compute_analysis_decision(
        visual_score=0.51,
        audio_score=0.41,
        disclosure_score=0.1,
        link_score=0.72,
        detected_brands=[
            {
                "name": "Nike",
                "confidence": 0.74,
                "source": "known,ocr",
                "detections": 3,
                "total_exposure_seconds": 4.2,
            }
        ],
        disclosure_markers=[],
        detected_keywords=["promo"],
        has_cta=True,
        has_commercial_links=True,
    )

    assert decision["has_advertising"] is True
    assert decision["confidence_score"] > 0.5


def test_classify_advertising_mentions_when_brand_signal_only():
    result = classify_advertising(
        has_advertising=False,
        disclosure_markers=[],
        detected_brands=[{"name": "Nike", "confidence": 0.9, "source": "text_content"}],
        detected_keywords=[],
    )

    assert result["classification"] == "mention"
