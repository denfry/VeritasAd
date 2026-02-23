"""Analysis domain dependencies - service and repository injection."""
from app.domains.analysis.repository import AnalysisRepository
from app.domains.analysis.service import AnalysisService
from app.services.video_processor import VideoProcessor
from app.services.disclosure_detector import DisclosureDetector
from app.core.config import settings

_repository: AnalysisRepository | None = None
_service: AnalysisService | None = None


def get_analysis_repository() -> AnalysisRepository:
    """Get AnalysisRepository singleton."""
    global _repository
    if _repository is None:
        _repository = AnalysisRepository()
    return _repository


def get_analysis_service() -> AnalysisService:
    """Get AnalysisService singleton with dependencies."""
    global _service
    if _service is None:
        _service = AnalysisService(
            repository=get_analysis_repository(),
            processor=VideoProcessor(),
            disclosure_detector=DisclosureDetector(use_llm=settings.USE_LLM),
        )
    return _service
