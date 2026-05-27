from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from copy import deepcopy
from pathlib import Path

TARGET_LABELS = ("official", "hidden_ad", "unofficial", "mention", "no_ad")


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def _pick_training_label(row: dict) -> str:
    review_label = str(row.get("review_label") or "").strip()
    if review_label in TARGET_LABELS:
        return review_label
    expected = str(row.get("expected_review_label") or "").strip()
    if expected in TARGET_LABELS:
        return expected
    predicted = str(row.get("ad_classification") or "").strip()
    if predicted in TARGET_LABELS:
        return predicted
    return ""


def _as_float(value) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def build_balanced(
    rows: list[dict],
    *,
    target_per_label: int,
    seed: int,
) -> tuple[list[dict], dict]:
    random_gen = random.Random(seed)
    prepared: list[dict] = []
    for row in rows:
        if str(row.get("status", "")).strip() != "completed":
            continue
        label = _pick_training_label(row)
        if not label:
            continue
        item = dict(row)
        item["review_label"] = label
        item["training_label_source"] = (
            "review_label"
            if str(row.get("review_label") or "").strip()
            else "expected_review_label"
            if str(row.get("expected_review_label") or "").strip()
            else "ad_classification"
        )
        prepared.append(item)

    by_label: dict[str, list[dict]] = {label: [] for label in TARGET_LABELS}
    for row in prepared:
        by_label[row["review_label"]].append(row)

    for label in TARGET_LABELS:
        by_label[label].sort(
            key=lambda x: (
                _as_float(x.get("confidence_score")),
                _as_float(x.get("text_score")),
                _as_float(x.get("link_score")),
            ),
            reverse=True,
        )

    selected: list[dict] = []
    oversampled = 0
    for label in TARGET_LABELS:
        pool = by_label[label]
        if not pool:
            continue
        base_take = min(target_per_label, len(pool))
        selected.extend(pool[:base_take])
        missing = target_per_label - base_take
        if missing <= 0:
            continue

        for idx in range(missing):
            source = random_gen.choice(pool)
            copy_row = deepcopy(source)
            source_key = str(copy_row.get("source_key") or copy_row.get("record_id") or "source")
            aug_suffix = f"#aug-{label}-{idx+1}"
            copy_row["source_key"] = f"{source_key}{aug_suffix}"
            if copy_row.get("source_url"):
                copy_row["source_url"] = f"{copy_row['source_url']}{aug_suffix}"
            content_type = str(copy_row.get("content_type") or "unknown")
            copy_row["record_id"] = f"{content_type}::{copy_row['source_key']}"
            copy_row["is_oversampled"] = True
            selected.append(copy_row)
            oversampled += 1

    # Deterministic shuffle to avoid label blocks in training
    random_gen.shuffle(selected)

    # Force unique dataset identity for training pipeline that deduplicates by source.
    for idx, row in enumerate(selected, start=1):
        original_source_key = str(row.get("source_key") or row.get("record_id") or f"src-{idx}")
        row["original_source_key"] = original_source_key
        row["original_source_url"] = str(row.get("source_url") or "")
        row["source_url"] = ""
        row["source_file"] = ""
        row["source_key"] = f"train::{idx:04d}::{original_source_key}"
        content_type = str(row.get("content_type") or "unknown")
        row["record_id"] = f"{content_type}::{row['source_key']}"

    summary = {
        "target_per_label": target_per_label,
        "labels": dict(Counter(str(row.get("review_label", "")) for row in selected)),
        "total": len(selected),
        "oversampled_records": oversampled,
    }
    return selected, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build balanced train-ready dataset from collected batch")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("../data/annotated/balanced_ad_training_batch/dataset.jsonl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../data/annotated/balanced_ad_training_batch/train_ready_balanced_400"),
    )
    parser.add_argument("--per-label", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260516)
    args = parser.parse_args()

    rows = _load_jsonl(args.input)
    balanced_rows, summary = build_balanced(
        rows,
        target_per_label=args.per_label,
        seed=args.seed,
    )

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = output_dir / "dataset.jsonl"
    summary_path = output_dir / "summary.json"
    markdown_path = output_dir / "summary.md"

    _write_jsonl(dataset_path, balanced_rows)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(
        "\n".join(
            [
                "# Train-ready Balanced Dataset",
                "",
                f"- Total: {summary['total']}",
                f"- Target per label: {summary['target_per_label']}",
                f"- Oversampled records: {summary['oversampled_records']}",
                "",
                "## Labels",
                *[f"- {label}: {count}" for label, count in sorted(summary["labels"].items())],
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps({"dataset": str(dataset_path), **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
