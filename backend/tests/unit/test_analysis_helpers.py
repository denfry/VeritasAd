import pytest
import sys
import types

# Stub optional LLM SDKs so helper imports do not fail during test collection.
sys.modules.setdefault("openai", types.SimpleNamespace(AsyncOpenAI=object))
sys.modules.setdefault("anthropic", types.SimpleNamespace(Anthropic=object))

from app.api.v1.analyze import _has_video_payload, _infer_source_type
from app.core.errors import ErrorCode
from app.models.database import SourceType
from app.services.video_download_errors import classify_processing_error


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://youtu.be/demo", SourceType.YOUTUBE),
        ("https://www.youtube.com/watch?v=demo", SourceType.YOUTUBE),
        ("https://t.me/channel/1", SourceType.TELEGRAM),
        ("https://instagram.com/p/demo", SourceType.INSTAGRAM),
        ("https://instagr.am/p/demo", SourceType.INSTAGRAM),
        ("https://www.tiktok.com/@demo/video/1", SourceType.TIKTOK),
        ("https://vk.com/video1", SourceType.VK),
        ("https://example.com/video.mp4", SourceType.URL),
        (None, SourceType.FILE),
    ],
)
def test_infer_source_type_matches_known_platforms(url, expected):
    assert _infer_source_type(url) == expected


@pytest.mark.parametrize(
    ("info", "expected"),
    [
        ({"duration": 12}, True),
        ({"duration": 0, "width": 1920}, True),
        ({"height": 1080}, True),
        ({"formats": [{"vcodec": "h264"}]}, True),
        ({"formats": [{"vcodec": "none"}]}, False),
        ({}, False),
    ],
)
def test_has_video_payload_detects_expected_shapes(info, expected):
    assert _has_video_payload(info) is expected


@pytest.mark.parametrize(
    ("raw_error", "expected_code", "expected_message_part"),
    [
        (
            "YouTube said: sign in to confirm you're not a bot in yt-dlp",
            ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "platform protection",
        ),
        (
            "ERROR: This video is unavailable",
            ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "not available for download",
        ),
        (
            "HTTP Error 429: Too Many Requests",
            ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "temporary platform or network limitation",
        ),
        (
            "HTTP Error 403: Forbidden while downloading fragment 218",
            ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "temporary platform or network limitation",
        ),
        (
            "yt-dlp failed: fragment not found; The downloaded file is empty",
            ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "temporary platform or network limitation",
        ),
        (
            "some unexpected ffmpeg failure",
            ErrorCode.PROCESSING_FAILED,
            "Could not process the video",
        ),
    ],
)
def test_classify_processing_error_maps_known_failures(
    raw_error, expected_code, expected_message_part
):
    result = classify_processing_error(raw_error)

    assert result["error_code"] == expected_code
    assert expected_message_part in result["user_message"]
