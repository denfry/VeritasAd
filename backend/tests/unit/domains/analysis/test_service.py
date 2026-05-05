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

    @pytest.mark.asyncio
    async def test_build_post_response_applies_enabled_model_scorer(self, service, mock_processor, mock_disclosure):
        mock_disclosure.analyze = AsyncMock(
            return_value={
                "markers": [],
                "score": 0.1,
                "has_disclosure": False,
                "discovered_brands": [],
            }
        )
        mock_processor.detect_brands_in_text.return_value = []
        service.ad_model_scorer = MagicMock()
        service.ad_model_scorer.score.return_value = {
            "model_version": "unit-model",
            "model_confidence": 0.91,
            "model_class_probabilities": {"hidden_ad": 0.91, "no_ad": 0.09},
            "ad_classification": "hidden_ad",
            "has_advertising": True,
        }

        with patch("app.domains.analysis.service.LinkDetector") as link_detector_cls:
            link_detector_cls.return_value.analyze.return_value = {
                "link_score": 0.8,
                "has_cta": True,
                "has_ad_signals": True,
                "cta_matches": ["buy"],
                "urls": ["https://example.test/deal"],
            }

            response = await service._build_post_response(
                "https://example.test/post",
                {
                    "id": "post-1",
                    "title": "Discount",
                    "description": "buy with promo",
                    "uploader": "creator",
                },
                SourceType.URL,
            )

        assert response["ad_classification"] == "hidden_ad"
        assert response["has_advertising"] is True
        assert response["model_version"] == "unit-model"
        assert response["model_confidence"] == pytest.approx(0.91)
