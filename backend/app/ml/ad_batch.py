from __future__ import annotations

import json
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from collections import Counter


@dataclass(frozen=True)
class BatchProfile:
    name: str
    language: str  # ISO 639-1 language code
    expected_label: str
    video_queries: tuple[str, ...]
    telegram_channels: tuple[str, ...] = ()
    reviewer_hint: str = ""


@dataclass(frozen=True)
class BatchPlan:
    output_dir: Path
    profiles: tuple[BatchProfile, ...]
    videos_per_profile: int
    posts_per_profile: int
    review_threshold: float
    empty_video_dir: Path

    @property
    def total_target_videos(self) -> int:
        return len(self.profiles) * self.videos_per_profile

    @property
    def total_target_posts(self) -> int:
        return len(self.profiles) * self.posts_per_profile

    @property
    def dataset_path(self) -> Path:
        return self.output_dir / "dataset.jsonl"

    @property
    def review_queue_path(self) -> Path:
        return self.output_dir / "review_queue.jsonl"

    @property
    def review_labels_path(self) -> Path:
        return self.output_dir / "review_labels.jsonl"

    @property
    def reviewed_path(self) -> Path:
        return self.output_dir / "reviewed.jsonl"

    @property
    def manifest_path(self) -> Path:
        return self.output_dir / "batch_manifest.json"

    @property
    def review_guide_path(self) -> Path:
        return self.output_dir / "review_guide.md"

    @property
    def dataset_csv_path(self) -> Path:
        return self.output_dir / "dataset.csv"

    @property
    def sources_path(self) -> Path:
        return self.output_dir / "sources.json"

    @property
    def summary_path(self) -> Path:
        return self.output_dir / "summary.md"


DEFAULT_BATCH_PROFILES: dict[str, BatchProfile] = {
    "official": BatchProfile(
        name="official",
        language="ru",
        expected_label="official",
        video_queries=(
            "#ad sponsored review promo code",
            "paid partnership #sponsored discount code",
            "sponsored by use code discount review",
        ),
        reviewer_hint="Paid promotion with an explicit disclosure marker such as #ad, #sponsored, ERID, or paid partnership.",
    ),
    "hidden_ad": BatchProfile(
        name="hidden_ad",
        language="ru",
        expected_label="hidden_ad",
        video_queries=(
            "affiliate link discount code review",
            "coupon code link in description review",
            "promo code exclusive discount no sponsored disclosure",
        ),
        reviewer_hint="Commercial CTA, affiliate/coupon link, or sales script without clear disclosure.",
    ),
    "unofficial": BatchProfile(
        name="unofficial",
        language="ru",
        expected_label="unofficial",
        video_queries=(
            "brand integration review without sponsor disclosure",
            "creator recommends product no disclosure",
            "ambassador review brand mention discount",
        ),
        reviewer_hint="Advertising intent is plausible, but official disclosure and hard affiliate evidence are absent.",
    ),
    "mention": BatchProfile(
        name="mention",
        language="ru",
        expected_label="mention",
        video_queries=(
            "tech review unboxing comparison",
            "product review no affiliate link",
            "brand news analysis review",
        ),
        reviewer_hint="Brand appears or is discussed, but the content is not primarily promotional.",
    ),
    "no_ad": BatchProfile(
        name="no_ad",
        language="ru",
        expected_label="no_ad",
        video_queries=(
            "tutorial how to build project",
            "news analysis today no sponsor",
            "educational explanation lecture",
        ),
        telegram_channels=("meduzalive", "tproger", "durov"),
        reviewer_hint="No meaningful brand promotion, CTA, disclosure, or commercial link evidence.",
    ),
}


def create_batch_plan(
    *,
    output_dir: Path,
    videos_per_profile: int,
    posts_per_profile: int,
    profiles: Sequence[BatchProfile] | None = None,
    review_threshold: float = 0.78,
    empty_video_dir: Path | None = None,
) -> BatchPlan:
    if videos_per_profile < 0 or posts_per_profile < 0:
        raise ValueError("profile targets must be non-negative")
    selected_profiles = tuple(profiles or DEFAULT_BATCH_PROFILES.values())
    if not selected_profiles:
        raise ValueError("at least one profile is required")
    return BatchPlan(
        output_dir=Path(output_dir),
        profiles=selected_profiles,
        videos_per_profile=videos_per_profile,
        posts_per_profile=posts_per_profile,
        review_threshold=review_threshold,
        empty_video_dir=Path(empty_video_dir) if empty_video_dir else Path(output_dir) / "_empty_video_source",
    )


def build_auto_annotate_commands(plan: BatchPlan) -> list[list[str]]:
    commands: list[list[str]] = []
    for profile in plan.profiles:
        profile_output = plan.output_dir / profile.name
        command = [
            sys.executable,
            "scripts/auto_annotate.py",
            "--target-videos",
            str(plan.videos_per_profile),
            "--target-posts",
            str(plan.posts_per_profile),
            "--output-dir",
            str(profile_output),
            "--local-video-dir",
            str(plan.empty_video_dir),
            "--review-threshold",
            str(plan.review_threshold),
            "--no-resume",
        ]
        for query in profile.video_queries:
            command.extend(["--video-query", query])
        for channel in profile.telegram_channels:
            command.extend(["--telegram-channel", channel])
        commands.append(command)
    return commands


def build_manifest(plan: BatchPlan) -> dict[str, object]:
    return {
        "output_dir": str(plan.output_dir),
        "dataset_path": str(plan.dataset_path),
        "review_queue_path": str(plan.review_queue_path),
        "review_labels_path": str(plan.review_labels_path),
        "reviewed_path": str(plan.reviewed_path),
        "videos_per_profile": plan.videos_per_profile,
        "posts_per_profile": plan.posts_per_profile,
        "total_target_videos": plan.total_target_videos,
        "total_target_posts": plan.total_target_posts,
        "profiles": [
            {
                "name": profile.name,
                "expected_label": profile.expected_label,
                "video_queries": list(profile.video_queries),
                "telegram_channels": list(profile.telegram_channels),
                "reviewer_hint": profile.reviewer_hint,
            }
            for profile in plan.profiles
        ],
    }


def build_review_guide(plan: BatchPlan) -> str:
    lines = [
        "# Ad Training Batch Review Guide",
        "",
        "## Labels",
        "- `official`: paid promotion with explicit disclosure such as `#ad`, `#sponsored`, ERID, or paid partnership.",
        "- `hidden_ad`: commercial CTA, affiliate/coupon link, or sales script without clear disclosure.",
        "- `unofficial`: likely advertising or endorsement, but without enough evidence for official or hidden advertising.",
        "- `mention`: brand mention or review without clear promotional intent.",
        "- `no_ad`: no meaningful ad signal.",
        "",
        "## Profile Hints",
    ]
    for profile in plan.profiles:
        lines.append(f"- `{profile.name}` expects `{profile.expected_label}`: {profile.reviewer_hint}")
    lines.extend(
        [
            "",
            "## Review Flow",
            f"1. Fill `{plan.review_labels_path.name}` with JSONL rows: `record_id`, `review_label`, and optional `notes`.",
            "2. Import labels after review:",
            "   ```bash",
            f"   python scripts/ml_pipeline.py import-labels {plan.dataset_path} {plan.review_labels_path} {plan.reviewed_path}",
            "   ```",
            "3. Split, train, and evaluate only after the reviewed labels are complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def combine_profile_records(profile: BatchProfile, records: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    combined: list[dict[str, object]] = []
    for record in records:
        if record.get("status") != "completed":
            continue
        row = dict(record)
        row["batch_profile"] = profile.name
        row["language"] = profile.language
        row["expected_review_label"] = profile.expected_label
        row["needs_review"] = True
        combined.append(row)
    return combined


def build_review_queue_rows(records: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in records:
        record_id = str(record.get("record_id") or "").strip()
        source_key = str(
            record.get("source_url")
            or record.get("source_file")
            or record.get("source_key")
            or record_id
        ).strip()
        if not record_id:
            continue
        rows.append(
            {
                "record_id": record_id,
                "source_key": source_key,
                "batch_profile": record.get("batch_profile", ""),
                "expected_review_label": record.get("expected_review_label", ""),
                "review_label": "",
                "title": record.get("title", ""),
                "transcript_excerpt": str(record.get("transcript") or "")[:1000],
                "notes": "",
            }
        )
    return rows


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def _flatten_record(record: dict[str, object]) -> dict[str, object]:
    return {
        "record_id": record.get("record_id", ""),
        "status": record.get("status", ""),
        "content_type": record.get("content_type", ""),
        "source_type": record.get("source_type", ""),
        "source_key": record.get("source_key", ""),
        "source_url": record.get("source_url", ""),
        "source_file": record.get("source_file", ""),
        "title": record.get("title", ""),
        "uploader": record.get("uploader", ""),
        "ad_classification": record.get("ad_classification", ""),
        "confidence_score": record.get("confidence_score", 0.0),
        "needs_review": record.get("needs_review", False),
        "review_reason": record.get("review_reason", ""),
        "error": record.get("error", ""),
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flattened = [_flatten_record(row) for row in rows]
    fieldnames = list(flattened[0].keys()) if flattened else list(_flatten_record({}).keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)


def _build_sources_manifest(plan: BatchPlan) -> dict[str, object]:
    return {
        "output_dir": str(plan.output_dir),
        "profiles": [profile.name for profile in plan.profiles],
        "videos_per_profile": plan.videos_per_profile,
        "posts_per_profile": plan.posts_per_profile,
        "total_target_videos": plan.total_target_videos,
        "total_target_posts": plan.total_target_posts,
        "review_threshold": plan.review_threshold,
    }


def _render_summary(records: list[dict[str, object]]) -> str:
    total = len(records)
    by_status = Counter(str(record.get("status", "unknown")) for record in records)
    by_label = Counter(str(record.get("ad_classification", "")) for record in records if record.get("ad_classification"))
    by_source = Counter(str(record.get("source_type", "unknown")) for record in records)
    by_content = Counter(str(record.get("content_type", "unknown")) for record in records)

    lines = [
        "# Balanced Ad Training Batch",
        "",
        "## Totals",
        f"- Total records: {total}",
        f"- Completed: {by_status.get('completed', 0)}",
        f"- Failed: {total - by_status.get('completed', 0)}",
        f"- Needs review: {sum(1 for record in records if bool(record.get('needs_review')))}",
        "",
        "## Distribution by Label",
    ]
    for label, count in sorted(by_label.items()):
        lines.append(f"- {label}: {count}")
    if not by_label:
        lines.append("- none")

    lines.extend(["", "## Distribution by Source Type"])
    for source_type, count in sorted(by_source.items()):
        lines.append(f"- {source_type}: {count}")

    lines.extend(["", "## Distribution by Content Type"])
    for content_type, count in sorted(by_content.items()):
        lines.append(f"- {content_type}: {count}")

    lines.extend(["", "## Status Breakdown"])
    for status, count in sorted(by_status.items()):
        lines.append(f"- {status}: {count}")

    return "\n".join(lines) + "\n"


def consolidate_profile_outputs(plan: BatchPlan) -> dict[str, int]:
    combined: list[dict[str, object]] = []
    seen_sources: set[str] = set()
    for profile in plan.profiles:
        records = _load_jsonl(plan.output_dir / profile.name / "dataset.jsonl")
        for row in combine_profile_records(profile, records):
            source_key = str(
                row.get("source_key")
                or row.get("source_url")
                or row.get("source_file")
                or row.get("record_id")
                or ""
            ).strip()
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            combined.append(row)

    review_rows = build_review_queue_rows(combined)
    dataset_count = _write_jsonl(plan.dataset_path, combined)
    queue_count = _write_jsonl(plan.review_queue_path, review_rows)
    _write_csv(plan.dataset_csv_path, combined)
    plan.sources_path.write_text(
        json.dumps(_build_sources_manifest(plan), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    plan.summary_path.write_text(_render_summary(combined), encoding="utf-8")
    failed_count = sum(1 for row in combined if str(row.get("status", "")) != "completed")
    return {
        "dataset_records": dataset_count,
        "review_queue_records": queue_count,
        "failed_records": failed_count,
    }


def write_batch_plan(plan: BatchPlan, commands: Iterable[Sequence[str]]) -> None:
    plan.output_dir.mkdir(parents=True, exist_ok=True)
    plan.empty_video_dir.mkdir(parents=True, exist_ok=True)
    plan.manifest_path.write_text(
        json.dumps({**build_manifest(plan), "commands": [list(command) for command in commands]}, indent=2),
        encoding="utf-8",
    )
    plan.review_guide_path.write_text(build_review_guide(plan), encoding="utf-8")
