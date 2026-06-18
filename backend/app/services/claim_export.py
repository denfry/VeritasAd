"""Claim export to JSONL / CSV (VeritasAd 2.0, M2).

Serializes a :class:`~app.schemas.claims.ClaimExtractionResult` into the dataset
row format defined in ``docs/research/datasets/claims/schema.md`` so model output
can seed the annotation corpus (roadmap §6 "экспорт в JSONL/CSV"; §11.3 format).

The API :class:`~app.schemas.claims.Claim` uses roadmap §7.3 field names; this
layer maps them onto the dataset field names (``fragment``/``modality``/
``raw_claim``) and stamps ``annotator_id`` with the extraction method so
auto-generated rows are distinguishable from human annotations.
"""
from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List

from app.schemas.claims import ClaimExtractionResult

# Dataset JSONL field order (schema.md "Формат записи") + checkworthiness_score.
DATASET_FIELDS: List[str] = [
    "content_id",
    "source_type",
    "source_url",
    "fragment",
    "modality",
    "timestamp_start",
    "timestamp_end",
    "raw_claim",
    "normalized_claim",
    "is_checkable",
    "claim_type",
    "risk_level",
    "checkworthiness_score",
    "brand",
    "annotator_id",
]


def claims_to_rows(result: ClaimExtractionResult) -> List[Dict[str, Any]]:
    """Map a result's claims onto dataset rows (schema.md field names)."""
    annotator_id = f"auto:{result.method.value}"
    if result.model:
        annotator_id = f"auto:{result.method.value}:{result.model}"

    rows: List[Dict[str, Any]] = []
    for claim in result.claims:
        rows.append(
            {
                "content_id": result.content_id or "",
                "source_type": result.source_type or "",
                "source_url": result.source_url or "",
                "fragment": claim.raw_text,
                "modality": claim.source_modality.value,
                "timestamp_start": claim.timestamp_start,
                "timestamp_end": claim.timestamp_end,
                "raw_claim": claim.raw_text,
                "normalized_claim": claim.normalized_claim,
                "is_checkable": claim.is_checkable,
                "claim_type": claim.claim_type.value,
                "risk_level": claim.risk_level.value,
                "checkworthiness_score": claim.checkworthiness_score,
                "brand": claim.brand or "",
                "annotator_id": annotator_id,
            }
        )
    return rows


def to_jsonl(result: ClaimExtractionResult) -> str:
    """Render claims as JSONL (one JSON object per line, UTF-8, no ASCII escaping)."""
    lines = [json.dumps(row, ensure_ascii=False) for row in claims_to_rows(result)]
    return "\n".join(lines) + ("\n" if lines else "")


def to_csv(result: ClaimExtractionResult) -> str:
    """Render claims as CSV with the dataset field header."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=DATASET_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in claims_to_rows(result):
        writer.writerow(row)
    return buffer.getvalue()
