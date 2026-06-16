from corpus.manifest import append_entries, existing_ids, load_manifest, stats
from corpus.schema import (
    DisclosureMatch, ManifestEntry, MarkerType, Platform,
    VideoRecord, WeakLabel, WeakLabelClass,
)


def _entry(video_id, label_class, markers=()):
    record = VideoRecord(video_id=video_id, platform=Platform.YOUTUBE,
                         url=f"https://x/{video_id}", description="d")
    label = WeakLabel(video_id=video_id, label=label_class, markers=list(markers))
    return ManifestEntry(record=record, label=label)


def test_append_then_load_roundtrip(tmp_path):
    path = tmp_path / "manifest.jsonl"
    marker = DisclosureMatch(MarkerType.ERID, "erid: AB12CD", value="AB12CD")
    append_entries(path, [_entry("a", WeakLabelClass.DISCLOSED_AD, [marker])])
    loaded = load_manifest(path)
    assert len(loaded) == 1
    assert loaded[0].record.video_id == "a"
    assert loaded[0].label.markers[0].value == "AB12CD"


def test_append_is_additive(tmp_path):
    path = tmp_path / "manifest.jsonl"
    append_entries(path, [_entry("a", WeakLabelClass.DISCLOSED_AD)])
    append_entries(path, [_entry("b", WeakLabelClass.UNLABELED)])
    assert {e.record.video_id for e in load_manifest(path)} == {"a", "b"}


def test_existing_ids(tmp_path):
    path = tmp_path / "manifest.jsonl"
    append_entries(path, [_entry("a", WeakLabelClass.UNLABELED)])
    assert existing_ids(path) == {"a"}


def test_existing_ids_on_missing_file(tmp_path):
    assert existing_ids(tmp_path / "nope.jsonl") == set()


def test_stats_counts_by_label_and_platform(tmp_path):
    entries = [
        _entry("a", WeakLabelClass.DISCLOSED_AD),
        _entry("b", WeakLabelClass.UNLABELED),
        _entry("c", WeakLabelClass.UNLABELED),
    ]
    result = stats(entries)
    assert result["total"] == 3
    assert result["by_label"] == {"disclosed_ad": 1, "unlabeled": 2}
    assert result["by_platform"] == {"youtube": 3}
    assert result["schema_version"]
