from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ml.ad_batch import (
    DEFAULT_BATCH_PROFILES,
    build_auto_annotate_commands,
    consolidate_profile_outputs,
    create_batch_plan,
    write_batch_plan,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare or run a balanced ad-training collection batch.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "annotated" / "balanced_ad_training_batch",
    )
    parser.add_argument("--videos-per-profile", type=int, default=10)
    parser.add_argument("--posts-per-profile", type=int, default=10)
    parser.add_argument("--review-threshold", type=float, default=0.78)
    parser.add_argument(
        "--profile",
        action="append",
        choices=tuple(DEFAULT_BATCH_PROFILES),
        help="Limit collection to one or more profiles. Defaults to all profiles.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run auto_annotate.py for each profile. Without this flag the command only writes a manifest and prints commands.",
    )
    parser.add_argument(
        "--consolidate-only",
        action="store_true",
        help="Skip collection and rebuild dataset.jsonl plus review_queue.jsonl from existing profile outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    profiles = (
        tuple(DEFAULT_BATCH_PROFILES[name] for name in args.profile)
        if args.profile
        else tuple(DEFAULT_BATCH_PROFILES.values())
    )
    plan = create_batch_plan(
        output_dir=args.output_dir,
        videos_per_profile=args.videos_per_profile,
        posts_per_profile=args.posts_per_profile,
        profiles=profiles,
        review_threshold=args.review_threshold,
    )
    commands = build_auto_annotate_commands(plan)
    write_batch_plan(plan, commands)

    print(f"manifest: {plan.manifest_path}")
    print(f"review guide: {plan.review_guide_path}")
    for command in commands:
        print(" ".join(command))

    if args.consolidate_only:
        result = consolidate_profile_outputs(plan)
        print(f"dataset records: {result['dataset_records']}")
        print(f"review queue records: {result['review_queue_records']}")
        return 0

    if not args.run:
        return 0

    for command in commands:
        completed = subprocess.run(command, cwd=BACKEND_ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    result = consolidate_profile_outputs(plan)
    print(f"dataset records: {result['dataset_records']}")
    print(f"review queue records: {result['review_queue_records']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
