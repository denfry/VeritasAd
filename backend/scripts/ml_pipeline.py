from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.ml.ad_dataset import (
    DatasetValidationError,
    export_review_queue,
    import_review_labels,
    load_records,
    split_records,
    write_jsonl,
)
from app.ml.ad_model import evaluate_records, train_classifier


def _write_split(output_dir: Path, name: str, records) -> None:
    write_jsonl(output_dir / f"{name}.jsonl", (record.raw for record in records))


def cmd_validate(args: argparse.Namespace) -> int:
    records = load_records(args.dataset)
    needs_review = sum(1 for record in records if record.needs_review)
    labels: dict[str, int] = {}
    for record in records:
        labels[record.label] = labels.get(record.label, 0) + 1
    print(json.dumps({"records": len(records), "needs_review": needs_review, "labels": labels}, indent=2))
    return 0


def cmd_split(args: argparse.Namespace) -> int:
    records = load_records(args.dataset)
    split = split_records(
        records,
        seed=args.seed,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_split(output_dir, "train", split.train)
    _write_split(output_dir, "val", split.val)
    _write_split(output_dir, "test", split.test)
    print(
        json.dumps(
            {"train": len(split.train), "val": len(split.val), "test": len(split.test)},
            indent=2,
        )
    )
    return 0


def cmd_export_review(args: argparse.Namespace) -> int:
    exported = export_review_queue(args.dataset, args.output)
    print(json.dumps({"exported": exported, "output": str(args.output)}, indent=2))
    return 0


def cmd_import_labels(args: argparse.Namespace) -> int:
    updated = import_review_labels(args.dataset, args.labels, args.output)
    print(json.dumps({"updated": updated, "output": str(args.output)}, indent=2))
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    train_records = load_records(args.train)
    model = train_classifier(
        train_records,
        version=args.version
        or f"ad-hybrid-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
    )
    model.save(args.output)
    result = {"model_version": model.version, "classes": model.classes, "output": str(args.output)}
    if args.eval:
        eval_records = load_records(args.eval)
        result["evaluation"] = evaluate_records(model, eval_records)
    print(json.dumps(result, indent=2))
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    from app.ml.ad_model import HybridAdClassifier

    model = HybridAdClassifier.load(args.model)
    records = load_records(args.dataset)
    print(json.dumps(evaluate_records(model, records), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VeritasAd reviewed dataset and ad model CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("dataset", type=Path)
    validate.set_defaults(func=cmd_validate)

    split = subparsers.add_parser("split")
    split.add_argument("dataset", type=Path)
    split.add_argument("output_dir", type=Path)
    split.add_argument("--seed", type=int, default=20260505)
    split.add_argument("--val-ratio", type=float, default=0.15)
    split.add_argument("--test-ratio", type=float, default=0.15)
    split.set_defaults(func=cmd_split)

    export_review = subparsers.add_parser("export-review")
    export_review.add_argument("dataset", type=Path)
    export_review.add_argument("output", type=Path)
    export_review.set_defaults(func=cmd_export_review)

    import_labels = subparsers.add_parser("import-labels")
    import_labels.add_argument("dataset", type=Path)
    import_labels.add_argument("labels", type=Path)
    import_labels.add_argument("output", type=Path)
    import_labels.set_defaults(func=cmd_import_labels)

    train = subparsers.add_parser("train")
    train.add_argument("train", type=Path)
    train.add_argument("output", type=Path)
    train.add_argument("--eval", type=Path)
    train.add_argument("--version")
    train.set_defaults(func=cmd_train)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("model", type=Path)
    evaluate.add_argument("dataset", type=Path)
    evaluate.set_defaults(func=cmd_evaluate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except DatasetValidationError as exc:
        parser.exit(2, f"dataset error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
