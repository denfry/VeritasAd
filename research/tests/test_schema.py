from corpus.schema import (
    DisclosureMatch, MarkerType, Platform, VideoRecord,
    WeakLabel, WeakLabelClass, ManifestEntry,
    entry_to_dict, entry_from_dict, SCHEMA_VERSION,
)


def _sample_entry() -> ManifestEntry:
    record = VideoRecord(
        video_id="vid1",
        platform=Platform.YOUTUBE,
        url="https://youtu.be/vid1",
        title="Обзор",
        description="erid: 2Vfnxw9ab на правах рекламы",
        channel="BloggerX",
        duration_sec=600.0,
        fetched_at="2026-06-16T10:00:00Z",
    )
    label = WeakLabel(
        video_id="vid1",
        label=WeakLabelClass.DISCLOSED_AD,
        markers=[DisclosureMatch(MarkerType.ERID, "erid: 2Vfnxw9ab", value="2Vfnxw9ab")],
        confidence=1.0,
        has_weak_signal=False,
    )
    return ManifestEntry(record=record, label=label)


def test_disclosure_text_joins_title_and_description():
    record = VideoRecord(video_id="v", platform=Platform.VK, url="u",
                         title="T", description="D")
    assert record.disclosure_text() == "T\nD"


def test_entry_roundtrip_through_dict():
    entry = _sample_entry()
    restored = entry_from_dict(entry_to_dict(entry))
    assert restored.record.video_id == "vid1"
    assert restored.record.platform == Platform.YOUTUBE
    assert restored.label.label == WeakLabelClass.DISCLOSED_AD
    assert restored.label.markers[0].marker_type == MarkerType.ERID
    assert restored.label.markers[0].value == "2Vfnxw9ab"
    assert restored.label.confidence == 1.0


def test_schema_version_is_exposed():
    assert SCHEMA_VERSION
