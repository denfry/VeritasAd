import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.ml.ad_dataset import (
    AD_CLASSES,
    DatasetValidationError,
    export_review_queue,
    import_review_labels,
    load_records,
    split_records,
    validate_record,
)


def _tmp_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / ".tmp" / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def _record(source_url: str, label: str = "hidden_ad", needs_review: bool = False) -> dict:
    return {
        "record_id": f"video::{source_url}",
        "source_url": source_url,
        "content_type": "video",
        "status": "completed",
        "title": "Sponsor segment",
        "description": "Use promo code DEAL10",
        "transcript": "This episode is sponsored by Example Brand.",
        "has_advertising": True,
        "ad_classification": label,
        "confidence_score": 0.82,
        "visual_score": 0.4,
        "audio_score": 0.6,
        "text_score": 0.8,
        "disclosure_score": 0.2,
        "link_score": 0.5,
        "detected_brands": [{"name": "Example Brand", "confidence": 0.9}],
        "detected_keywords": ["promo"],
        "disclosure_text": [],
        "cta_matches": ["promo code"],
        "commercial_urls": ["https://example.test/deal"],
        "review_label": label,
        "needs_review": needs_review,
    }


def test_validate_record_normalizes_supported_class_and_features():
    normalized = validate_record(_record("https://example.test/a", label="official"))

    assert normalized.label == "official"
    assert normalized.source_key == "https://example.test/a"
    assert normalized.features["confidence_score"] == pytest.approx(0.82)
    assert normalized.features["brand_count"] == pytest.approx(1.0)
    assert normalized.text.startswith("Sponsor segment")
    assert normalized.needs_review is False
    assert normalized.has_text_encoding_warning is False
    assert "official" in AD_CLASSES


def test_validate_record_rejects_unknown_review_label():
    record = _record("https://example.test/a")
    record["review_label"] = "maybe_ad"

    with pytest.raises(DatasetValidationError, match="unsupported label"):
        validate_record(record)


def test_validate_record_flags_mojibake_transcript_for_review():
    record = _record("https://example.test/a", needs_review=False)
    record["transcript"] = "РџСЂРѕРјРѕРєРѕРґ Рё СЃРєРёРґРєР°"

    normalized = validate_record(record)

    assert normalized.needs_review is True
    assert normalized.has_text_encoding_warning is True


def test_load_records_reports_duplicate_source_keys():
    tmp_path = _tmp_dir()
    dataset_path = tmp_path / "dataset.jsonl"
    rows = [_record("https://example.test/a"), _record("https://example.test/a")]
    dataset_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    with pytest.raises(DatasetValidationError, match="duplicate source"):
        load_records(dataset_path)


def test_split_records_keeps_same_source_out_of_multiple_splits():
    rows = [
        validate_record(_record("https://example.test/a", "hidden_ad")),
        validate_record(_record("https://example.test/b", "official")),
        validate_record(_record("https://example.test/c", "mention")),
        validate_record(_record("https://example.test/d", "no_ad")),
        validate_record(_record("https://example.test/e", "unofficial")),
    ]

    split = split_records(rows, seed=42, val_ratio=0.2, test_ratio=0.2)
    train_sources = {record.source_key for record in split.train}
    val_sources = {record.source_key for record in split.val}
    test_sources = {record.source_key for record in split.test}

    assert train_sources.isdisjoint(val_sources)
    assert train_sources.isdisjoint(test_sources)
    assert val_sources.isdisjoint(test_sources)
    assert len(split.train) == 3
    assert len(split.val) == 1
    assert len(split.test) == 1


def test_review_queue_export_and_import_labels():
    tmp_path = _tmp_dir()
    dataset_path = tmp_path / "dataset.jsonl"
    queue_path = tmp_path / "review_queue.jsonl"
    labels_path = tmp_path / "labels.jsonl"
    output_path = tmp_path / "reviewed.jsonl"

    rows = [
        _record("https://example.test/a", "hidden_ad", needs_review=True),
        _record("https://example.test/b", "no_ad", needs_review=False),
    ]
    dataset_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    exported = export_review_queue(dataset_path, queue_path)
    assert exported == 1
    exported_rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines()]
    assert exported_rows[0]["record_id"] == "video::https://example.test/a"
    assert "transcript_excerpt" in exported_rows[0]

    labels_path.write_text(
        json.dumps({"record_id": "video::https://example.test/a", "review_label": "official"}),
        encoding="utf-8",
    )
    updated = import_review_labels(dataset_path, labels_path, output_path)

    assert updated == 1
    reviewed_rows = [
        json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    assert reviewed_rows[0]["review_label"] == "official"
    assert reviewed_rows[0]["needs_review"] is False
