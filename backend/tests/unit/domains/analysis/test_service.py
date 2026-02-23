"""Unit tests for AnalysisService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domains.analysis.service import AnalysisService, _infer_source_type, _has_video_payload
from app.domains.analysis.repository import AnalysisRepository
from app.models.database import SourceType


class TestInferSourceType:
    """Tests for _infer_source_type helper."""

    def test_file_when_no_url(self):
        assert _infer_source_type(None) == SourceType.FILE

    def test_youtube(self):
        assert _infer_source_type("https://youtube.com/watch?v=xxx") == SourceType.YOUTUBE
        assert _infer_source_type("https://youtu.be/xxx") == SourceType.YOUTUBE

    def test_telegram(self):
        assert _infer_source_type("https://t.me/channel/123") == SourceType.TELEGRAM

    def test_instagram(self):
        assert _infer_source_type("https://instagram.com/p/xxx") == SourceType.INSTAGRAM

    def test_tiktok(self):
        assert _infer_source_type("https://tiktok.com/@user/video/123") == SourceType.TIKTOK

    def test_vk(self):
        assert _infer_source_type("https://vk.com/video123") == SourceType.VK
        assert _infer_source_type("https://vk.ru/video123") == SourceType.VK

    def test_generic_url(self):
        assert _infer_source_type("https://example.com/video.mp4") == SourceType.URL


class TestHasVideoPayload:
    """Tests for _has_video_payload helper."""

    def test_has_duration(self):
        assert _has_video_payload({"duration": 120}) is True
        assert _has_video_payload({"duration": 60.5}) is True

    def test_has_width_height(self):
        assert _has_video_payload({"width": 1920, "height": 1080}) is True

    def test_has_video_format(self):
        assert _has_video_payload({
            "formats": [{"vcodec": "h264"}]
        }) is True

    def test_no_video(self):
        assert _has_video_payload({"duration": 0}) is False
        assert _has_video_payload({"formats": [{"vcodec": "none"}]}) is False
        assert _has_video_payload({}) is False


class TestAnalysisService:
    """Tests for AnalysisService."""

    @pytest.fixture
    def mock_repository(self):
        repo = MagicMock(spec=AnalysisRepository)
        repo.create = AsyncMock()
        repo.get_by_task_id = AsyncMock()
        return repo

    @pytest.fixture
    def mock_processor(self):
        return MagicMock()

    @pytest.fixture
    def mock_disclosure(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repository, mock_processor, mock_disclosure):
        return AnalysisService(
            repository=mock_repository,
            processor=mock_processor,
            disclosure_detector=mock_disclosure,
        )
