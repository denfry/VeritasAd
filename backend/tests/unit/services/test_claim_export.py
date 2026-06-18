"""Tests for claim export to JSONL / CSV (VeritasAd 2.0, M2 roadmap §11.3)."""
import csv
import io
import json

from app.schemas.claims import (
    Claim,
    ClaimExtractionResult,
    ClaimType,
    ExtractionMethod,
    RiskLevel,
    SourceModality,
)
from app.services.claim_export import DATASET_FIELDS, to_csv, to_jsonl


def _result() -> ClaimExtractionResult:
    return ClaimExtractionResult(
        claims=[
            Claim(
                id="claim_001",
                raw_text="Скидка до 70%",
                normalized_claim="Скидка на товар достигает 70%",
                source_modality=SourceModality.OCR,
                claim_type=ClaimType.QUANTITATIVE,
                is_checkable=True,
                checkworthiness_score=0.5,
                risk_level=RiskLevel.MEDIUM,
                brand="Acme",
            ),
            Claim(
                id="claim_002",
                raw_text="Кэшбек 16% годовых",
                normalized_claim="Годовая ставка составляет 16%",
                source_modality=SourceModality.ASR,
                claim_type=ClaimType.FINANCIAL,
                is_checkable=True,
                checkworthiness_score=0.7,
                risk_level=RiskLevel.HIGH,
            ),
        ],
        method=ExtractionMethod.RULE_BASED,
        content_id="vid-1",
        source_type="video",
        source_url="https://example.com/v",
    )


def test_to_jsonl_one_object_per_claim():
    out = to_jsonl(_result())
    lines = out.strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        json.loads(line)  # each line is a standalone JSON object


def test_to_jsonl_uses_dataset_field_names():
    out = to_jsonl(_result())
    row = json.loads(out.strip().splitlines()[0])

    # Dataset field names (not the API schema names).
    assert row["content_id"] == "vid-1"
    assert row["fragment"] == "Скидка до 70%"
    assert row["modality"] == "ocr"
    assert row["raw_claim"] == "Скидка до 70%"
    assert row["claim_type"] == "quantitative"
    assert row["risk_level"] == "medium"
    assert row["checkworthiness_score"] == 0.5
    assert row["brand"] == "Acme"


def test_to_jsonl_annotator_id_is_auto_rule_based():
    out = to_jsonl(_result())
    row = json.loads(out.strip().splitlines()[0])
    assert row["annotator_id"] == "auto:rule_based"


def test_to_jsonl_empty_result_is_empty_string():
    assert to_jsonl(ClaimExtractionResult()) == ""


def test_to_csv_has_header_row():
    out = to_csv(_result())
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == DATASET_FIELDS


def test_to_csv_one_data_row_per_claim():
    out = to_csv(_result())
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[0]["modality"] == "ocr"
    assert rows[0]["annotator_id"] == "auto:rule_based"
