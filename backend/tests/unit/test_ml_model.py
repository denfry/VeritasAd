from pathlib import Path
from uuid import uuid4

import pytest

from app.ml.ad_dataset import validate_record
from app.ml.ad_model import HybridAdClassifier, evaluate_records, train_classifier
from app.services.ad_model_scorer import AdModelScorer


def _tmp_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / ".tmp" / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def _record(source_url: str, label: str, transcript: str, **scores) -> dict:
    return {
        "record_id": f"post::{source_url}",
        "source_url": source_url,
        "content_type": "post",
        "status": "completed",
        "title": transcript[:40],
        "description": transcript,
        "transcript": transcript,
        "has_advertising": label not in {"no_ad", "mention"},
        "ad_classification": label,
        "confidence_score": scores.get("confidence_score", 0.5),
        "visual_score": scores.get("visual_score", 0.0),
        "audio_score": scores.get("audio_score", 0.0),
        "text_score": scores.get("text_score", 0.0),
        "disclosure_score": scores.get("disclosure_score", 0.0),
        "link_score": scores.get("link_score", 0.0),
        "detected_brands": scores.get("detected_brands", []),
        "detected_keywords": scores.get("detected_keywords", []),
        "disclosure_text": scores.get("disclosure_text", []),
        "cta_matches": scores.get("cta_matches", []),
        "commercial_urls": scores.get("commercial_urls", []),
        "review_label": label,
        "needs_review": False,
    }


def test_train_classifier_predicts_class_probabilities_and_roundtrips():
    tmp_path = _tmp_dir()
    records = [
        validate_record(_record("https://example.test/ad1", "official", "sponsored promo code", disclosure_score=0.9)),
        validate_record(_record("https://example.test/ad2", "hidden_ad", "buy now discount link", link_score=0.9)),
        validate_record(_record("https://example.test/no1", "no_ad", "daily vlog no brands", confidence_score=0.1)),
        validate_record(_record("https://example.test/no2", "mention", "I bought a Nike shirt", detected_brands=[{"name": "Nike"}])),
    ]

    model = train_classifier(records, version="unit-test-model")
    prediction = model.predict(validate_record(_record("https://example.test/new", "hidden_ad", "promo discount link", link_score=0.8)))

    assert prediction.model_version == "unit-test-model"
    assert set(prediction.class_probabilities) == set(model.classes)
    assert sum(prediction.class_probabilities.values()) == pytest.approx(1.0)
    assert prediction.predicted_class in model.classes

    artifact_path = tmp_path / "ad-model.json"
    model.save(artifact_path)
    loaded = HybridAdClassifier.load(artifact_path)
    loaded_prediction = loaded.predict(records[0])

    assert loaded.version == "unit-test-model"
    assert loaded_prediction.predicted_class in loaded.classes


def test_evaluate_records_returns_per_class_metrics():
    records = [
        validate_record(_record("https://example.test/ad1", "official", "sponsored promo code", disclosure_score=0.9)),
        validate_record(_record("https://example.test/ad2", "hidden_ad", "buy now discount link", link_score=0.9)),
        validate_record(_record("https://example.test/no1", "no_ad", "daily vlog", confidence_score=0.1)),
    ]
    model = train_classifier(records, version="metrics-test")

    report = evaluate_records(model, records)

    assert report["total"] == 3
    assert 0.0 <= report["accuracy"] <= 1.0
    assert "official" in report["per_class"]
    assert {"precision", "recall", "f1", "support"} <= set(report["per_class"]["official"])


def test_ad_model_scorer_maps_prediction_to_existing_contract():
    tmp_path = _tmp_dir()
    records = [
        validate_record(_record("https://example.test/ad1", "hidden_ad", "promo discount link", link_score=0.9)),
        validate_record(_record("https://example.test/no1", "no_ad", "plain educational content", confidence_score=0.1)),
    ]
    artifact_path = tmp_path / "ad-model.json"
    train_classifier(records, version="scorer-test").save(artifact_path)

    scorer = AdModelScorer(artifact_path=artifact_path, enabled=True)
    result = scorer.score(
        {
            "title": "promo discount",
            "description": "buy now",
            "transcript": "promo discount link",
            "confidence_score": 0.8,
            "link_score": 0.9,
            "detected_brands": [],
            "detected_keywords": ["promo"],
            "disclosure_text": [],
            "cta_matches": ["buy"],
            "commercial_urls": ["https://example.test/deal"],
        }
    )

    assert result is not None
    assert result["model_version"] == "scorer-test"
    assert result["ad_classification"] in {"hidden_ad", "no_ad"}
    assert isinstance(result["has_advertising"], bool)
    assert 0.0 <= result["model_confidence"] <= 1.0


def test_ad_model_scorer_returns_none_when_artifact_missing():
    tmp_path = _tmp_dir()
    scorer = AdModelScorer(artifact_path=tmp_path / "missing.json", enabled=True)

    assert scorer.score({"title": "anything"}) is None
