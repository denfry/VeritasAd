from corpus.labeler import build_weak_label
from corpus.schema import Platform, VideoRecord, WeakLabelClass


def _record(desc: str, title: str = "") -> VideoRecord:
    return VideoRecord(video_id="v", platform=Platform.YOUTUBE, url="u",
                       title=title, description=desc)


def test_erid_makes_disclosed_ad_with_full_confidence():
    label = build_weak_label(_record("erid: 2Vfnxw9ab"))
    assert label.label == WeakLabelClass.DISCLOSED_AD
    assert label.confidence == 1.0


def test_phrase_only_is_disclosed_but_lower_confidence():
    label = build_weak_label(_record("видео на правах рекламы"))
    assert label.label == WeakLabelClass.DISCLOSED_AD
    assert 0.5 < label.confidence < 1.0


def test_weak_only_signal_stays_unlabeled():
    label = build_weak_label(_record("выпуск при поддержке друга"))
    assert label.label == WeakLabelClass.UNLABELED
    assert label.has_weak_signal is True
    assert label.confidence == 0.0


def test_clean_video_is_unlabeled_without_weak_signal():
    label = build_weak_label(_record("гулял в парке"))
    assert label.label == WeakLabelClass.UNLABELED
    assert label.has_weak_signal is False


def test_label_carries_video_id():
    rec = VideoRecord(video_id="abc", platform=Platform.VK, url="u",
                      description="erid: ABCDEF12")
    assert build_weak_label(rec).video_id == "abc"
