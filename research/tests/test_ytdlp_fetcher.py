import json
from pathlib import Path

from corpus.fetchers.ytdlp_fetcher import parse_ytdlp_info, platform_from_info
from corpus.schema import Platform

FIXTURE = Path(__file__).parent / "fixtures" / "ytdlp_info_sample.json"


def _info():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parse_maps_core_fields():
    rec = parse_ytdlp_info(_info(), fetched_at="2026-06-16T10:00:00Z")
    assert rec.video_id == "abc123"
    assert rec.platform == Platform.YOUTUBE
    assert rec.url == "https://www.youtube.com/watch?v=abc123"
    assert rec.title == "Большой обзор смартфона"
    assert "erid:" in rec.description
    assert rec.channel == "TechBlogger"
    assert rec.duration_sec == 743.0
    assert rec.fetched_at == "2026-06-16T10:00:00Z"


def test_platform_detection():
    assert platform_from_info({"extractor_key": "VKVideo"}) == Platform.VK
    assert platform_from_info({"extractor_key": "Rutube"}) == Platform.RUTUBE
    assert platform_from_info({"extractor": "youtube"}) == Platform.YOUTUBE
    assert platform_from_info({"extractor_key": "SomethingElse"}) == Platform.UNKNOWN


def test_missing_fields_are_tolerated():
    rec = parse_ytdlp_info({"id": "x"}, fetched_at="t")
    assert rec.video_id == "x"
    assert rec.title == ""
    assert rec.duration_sec is None
    assert rec.platform == Platform.UNKNOWN
