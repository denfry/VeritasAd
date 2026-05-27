from app.ml.ad_batch import (
    DEFAULT_BATCH_PROFILES,
    build_auto_annotate_commands,
    build_review_queue_rows,
    build_review_guide,
    combine_profile_records,
    consolidate_profile_outputs,
    create_batch_plan,
)


def test_create_batch_plan_selects_balanced_profiles():
    output_dir = _path("balanced_batch")

    plan = create_batch_plan(output_dir=output_dir, videos_per_profile=3, posts_per_profile=2)

    assert {profile.name for profile in plan.profiles} == {
        "official",
        "hidden_ad",
        "mention",
        "no_ad",
        "unofficial",
    }
    assert plan.total_target_videos == 15
    assert plan.total_target_posts == 10
    assert plan.review_queue_path == output_dir / "review_queue.jsonl"


def test_build_auto_annotate_commands_use_profile_queries_and_empty_local_dir():
    output_dir = _path("batch")
    empty_video_dir = _path("empty-video-source")
    plan = create_batch_plan(
        output_dir=output_dir,
        videos_per_profile=2,
        posts_per_profile=0,
        profiles=(DEFAULT_BATCH_PROFILES["official"], DEFAULT_BATCH_PROFILES["hidden_ad"]),
        empty_video_dir=empty_video_dir,
    )

    commands = build_auto_annotate_commands(plan)

    assert len(commands) == 2
    assert commands[0][0:2] == ["python", "scripts/auto_annotate.py"]
    assert "--target-videos" in commands[0]
    assert commands[0][commands[0].index("--target-videos") + 1] == "2"
    assert "--target-posts" in commands[0]
    assert commands[0][commands[0].index("--target-posts") + 1] == "0"
    assert "--local-video-dir" in commands[0]
    assert commands[0][commands[0].index("--local-video-dir") + 1] == str(empty_video_dir)
    assert "#ad sponsored review promo code" in commands[0]
    assert "affiliate link discount code review" in commands[1]


def test_review_guide_contains_label_definitions_and_import_command():
    plan = create_batch_plan(output_dir=_path("batch"), videos_per_profile=1, posts_per_profile=1)

    guide = build_review_guide(plan)

    assert "official" in guide
    assert "hidden_ad" in guide
    assert "review_labels.jsonl" in guide
    assert "ml_pipeline.py import-labels" in guide


def test_combine_profile_records_adds_expected_label_and_skips_failed():
    profile = DEFAULT_BATCH_PROFILES["hidden_ad"]
    rows = combine_profile_records(
        profile,
        [
            {"status": "completed", "record_id": "video::1", "title": "Coupon code"},
            {"status": "failed", "record_id": "video::2", "title": "Broken"},
        ],
    )

    assert len(rows) == 1
    assert rows[0]["batch_profile"] == "hidden_ad"
    assert rows[0]["expected_review_label"] == "hidden_ad"
    assert rows[0]["needs_review"] is True


def test_build_review_queue_rows_keeps_expected_label_as_hint_only():
    rows = build_review_queue_rows(
        [
            {
                "record_id": "video::1",
                "source_url": "https://example.test/video",
                "title": "Coupon code",
                "expected_review_label": "hidden_ad",
                "batch_profile": "hidden_ad",
                "transcript": "Use the link in description",
            }
        ]
    )

    assert rows == [
        {
            "record_id": "video::1",
            "source_key": "https://example.test/video",
            "batch_profile": "hidden_ad",
            "expected_review_label": "hidden_ad",
            "review_label": "",
            "title": "Coupon code",
            "transcript_excerpt": "Use the link in description",
            "notes": "",
        }
    ]


def test_consolidate_profile_outputs_writes_dataset_artifacts_and_deduplicates_sources():
    output_dir = _path("consolidate")
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = (DEFAULT_BATCH_PROFILES["official"], DEFAULT_BATCH_PROFILES["hidden_ad"])
    plan = create_batch_plan(
        output_dir=output_dir,
        videos_per_profile=1,
        posts_per_profile=1,
        profiles=profiles,
    )

    _write_jsonl(
        output_dir / "official" / "dataset.jsonl",
        [
            {
                "status": "completed",
                "record_id": "video::a",
                "source_key": "https://example.test/a",
                "content_type": "video",
                "source_type": "youtube",
                "ad_classification": "official",
            }
        ],
    )
    _write_jsonl(
        output_dir / "hidden_ad" / "dataset.jsonl",
        [
            {
                "status": "completed",
                "record_id": "video::a2",
                "source_key": "https://example.test/a",
                "content_type": "video",
                "source_type": "youtube",
                "ad_classification": "hidden_ad",
            },
            {
                "status": "completed",
                "record_id": "post::b",
                "source_key": "https://t.me/channel/1",
                "content_type": "post",
                "source_type": "telegram",
                "ad_classification": "mention",
            },
        ],
    )

    result = consolidate_profile_outputs(plan)

    assert result["dataset_records"] == 2
    assert result["review_queue_records"] == 2
    assert plan.dataset_csv_path.exists()
    assert plan.sources_path.exists()
    assert plan.summary_path.exists()


def _path(value: str):
    from pathlib import Path

    return Path(__file__).resolve().parents[2] / ".test-temp" / "ad-batch" / value


def _write_jsonl(path, rows):
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
