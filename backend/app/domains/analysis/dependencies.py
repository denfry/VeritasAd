"""Analysis domain dependencies - service and repository injection."""
from typing import TYPE_CHECKING, Any

from app.core.config import settings

if TYPE_CHECKING:
    from app.domains.analysis.repository import AnalysisRepository
    from app.domains.analysis.service import AnalysisService

_repository: "AnalysisRepository | None" = None
_service: "AnalysisService | None" = None


def get_analysis_repository() -> "AnalysisRepository":
    """Get AnalysisRepository singleton."""
    global _repository
    if _repository is None:
        from app.domains.analysis.repository import AnalysisRepository

        _repository = AnalysisRepository()
    return _repository


def get_analysis_service() -> "AnalysisService":
    """Get AnalysisService singleton with dependencies."""
    global _service
    if _service is None:
        # Delay heavy ML imports until the analysis service is actually needed.
        from app.domains.analysis.service import AnalysisService
        from app.services.disclosure_detector import DisclosureDetector
        from app.services.video_processor import VideoProcessor

        _service = AnalysisService(
            repository=get_analysis_repository(),
            processor=VideoProcessor(),
            disclosure_detector=DisclosureDetector(use_llm=settings.USE_LLM),
        )
    return _service
