from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


AD_CLASSES = ("no_ad", "mention", "official", "unofficial", "hidden_ad")
NUMERIC_FEATURE_KEYS = (
    "confidence_score",
    "visual_score",
    "audio_score",
    "text_score",
    "disclosure_score",
    "link_score",
)


class DatasetValidationError(ValueError):
    """Raised when a dataset record cannot be used for reviewed training."""


@dataclass(frozen=True)
class NormalizedAdRecord:
    raw: dict[str, Any]
    record_id: str
    source_key: str
    label: str
    text: str
    features: dict[str, float]
    needs_review: bool
    has_text_encoding_warning: bool


@dataclass(frozen=True)
class DatasetSplit:
    train: list[NormalizedAdRecord]
    val: list[NormalizedAdRecord]
    test: list[NormalizedAdRecord]


def _as_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _make_record_id(record: dict[str, Any]) -> str:
    explicit_id = str(record.get("record_id") or "").strip()
    if explicit_id:
        return explicit_id
    source = _source_key(record)
    content_type = str(record.get("content_type") or "unknown").strip() or "unknown"
    return f"{content_type}::{source}"


def _source_key(record: dict[str, Any]) -> str:
    for key in ("source_url", "source_file", "source_key", "file_path"):
        value = str(record.get(key) or "").strip()
        if value:
            return value
    record_id = str(record.get("record_id") or "").strip()
    if record_id:
        return record_id
    raise DatasetValidationError("record must include a source URL, file, key, or record_id")


def _label(record: dict[str, Any]) -> str:
    label = str(record.get("review_label") or record.get("ad_classification") or "").strip()
    if label not in AD_CLASSES:
        raise DatasetValidationError(f"unsupported label: {label or '<empty>'}")
    return label


def _text(record: dict[str, Any]) -> str:
    parts = [
        str(record.get("title") or ""),
        str(record.get("description") or ""),
        str(record.get("transcript") or ""),
    ]
    brand_names = [
        str(brand.get("name") or "")
        for brand in _as_list(record.get("detected_brands"))
        if isinstance(brand, dict)
    ]
    keyword_text = " ".join(str(item) for item in _as_list(record.get("detected_keywords")))
    return "\n".join(part for part in [*parts, " ".join(brand_names), keyword_text] if part).strip()


def has_mojibake(text: str) -> bool:
    if not text:
        return False
    suspicious_tokens = ("Р", "С", "Ð", "Ñ", "�")
    suspicious = sum(text.count(token) for token in suspicious_tokens)
    return suspicious >= 6 and suspicious / max(len(text), 1) > 0.08


def _features(record: dict[str, Any]) -> dict[str, float]:
    features = {key: _as_float(record.get(key)) for key in NUMERIC_FEATURE_KEYS}
    features.update(
        {
            "brand_count": float(len(_as_list(record.get("detected_brands")))),
            "keyword_count": float(len(_as_list(record.get("detected_keywords")))),
            "disclosure_marker_count": float(len(_as_list(record.get("disclosure_text")))),
            "cta_count": float(len(_as_list(record.get("cta_matches")))),
            "commercial_url_count": float(len(_as_list(record.get("commercial_urls")))),
            "has_advertising": 1.0 if bool(record.get("has_advertising")) else 0.0,
        }
    )
    return features


def validate_record(record: dict[str, Any]) -> NormalizedAdRecord:
    label = _label(record)
    text = _text(record)
    encoding_warning = has_mojibake(text)
    needs_review = bool(record.get("needs_review")) or encoding_warning
    source_key = _source_key(record)

    return NormalizedAdRecord(
        raw=dict(record),
        record_id=_make_record_id(record),
        source_key=source_key,
        label=label,
        text=text,
        features=_features(record),
        needs_review=needs_review,
        has_text_encoding_warning=encoding_warning,
    )


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DatasetValidationError(f"invalid JSON on line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise DatasetValidationError(f"line {line_number} must be a JSON object")
        yield value


def load_records(path: str | Path) -> list[NormalizedAdRecord]:
    dataset_path = Path(path)
    records: list[NormalizedAdRecord] = []
    seen_sources: set[str] = set()

    for raw in _iter_jsonl(dataset_path):
        record = validate_record(raw)
        if record.source_key in seen_sources:
            raise DatasetValidationError(f"duplicate source: {record.source_key}")
        seen_sources.add(record.source_key)
        records.append(record)

    return records


def split_records(
    records: list[NormalizedAdRecord],
    *,
    seed: int = 20260505,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> DatasetSplit:
    if val_ratio < 0 or test_ratio < 0 or val_ratio + test_ratio >= 1:
        raise DatasetValidationError("val_ratio and test_ratio must be non-negative and sum to < 1")

    by_source: dict[str, NormalizedAdRecord] = {}
    for record in records:
        if record.source_key in by_source:
            raise DatasetValidationError(f"duplicate source: {record.source_key}")
        by_source[record.source_key] = record

    shuffled = list(by_source.values())
    random.Random(seed).shuffle(shuffled)
    total = len(shuffled)
    test_count = int(round(total * test_ratio))
    val_count = int(round(total * val_ratio))
    if total >= 3 and test_ratio > 0:
        test_count = max(1, test_count)
    if total >= 3 and val_ratio > 0:
        val_count = max(1, val_count)
    if val_count + test_count >= total and total > 0:
        overflow = val_count + test_count - total + 1
        val_count = max(0, val_count - overflow)

    test = shuffled[:test_count]
    val = shuffled[test_count : test_count + val_count]
    train = shuffled[test_count + val_count :]
    return DatasetSplit(train=train, val=val, test=test)


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> int:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def export_review_queue(dataset_path: str | Path, output_path: str | Path) -> int:
    records = load_records(dataset_path)
    rows = []
    for record in records:
        if not record.needs_review:
            continue
        rows.append(
            {
                "record_id": record.record_id,
                "source_key": record.source_key,
                "current_label": record.label,
                "review_label": "",
                "needs_review": True,
                "encoding_warning": record.has_text_encoding_warning,
                "title": record.raw.get("title", ""),
                "description_excerpt": str(record.raw.get("description") or "")[:500],
                "transcript_excerpt": str(record.raw.get("transcript") or "")[:1000],
            }
        )
    return write_jsonl(output_path, rows)


def import_review_labels(
    dataset_path: str | Path,
    labels_path: str | Path,
    output_path: str | Path,
) -> int:
    label_updates: dict[str, str] = {}
    for row in _iter_jsonl(Path(labels_path)):
        record_id = str(row.get("record_id") or "").strip()
        label = str(row.get("review_label") or "").strip()
        if not record_id:
            raise DatasetValidationError("review label row missing record_id")
        if label not in AD_CLASSES:
            raise DatasetValidationError(f"unsupported label: {label or '<empty>'}")
        label_updates[record_id] = label

    updated = 0
    output_rows: list[dict[str, Any]] = []
    for row in _iter_jsonl(Path(dataset_path)):
        record_id = _make_record_id(row)
        if record_id in label_updates:
            row = dict(row)
            row["review_label"] = label_updates[record_id]
            row["needs_review"] = False
            updated += 1
        output_rows.append(row)

    write_jsonl(output_path, output_rows)
    return updated
