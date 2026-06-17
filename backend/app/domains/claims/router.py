"""Claims domain router - verifiable advertising claim extraction (VeritasAd 2.0, M2).

On-demand endpoints (roadmap §7.4, §14 Milestone 2):

* ``POST /api/v1/claims/extract`` — extract claims from raw multimodal signals.
* ``POST /api/v1/claims/from-analysis/{task_id}`` — extract from a stored analysis.
* ``GET  /api/v1/claims/{task_id}`` — return previously persisted claims.
* ``GET  /api/v1/claims/{task_id}/export`` — download claims as JSONL or CSV.

Extraction is on-demand and additive: it never alters the existing analysis
verdict and only writes ``Analysis.claims`` when ``persist`` is requested.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.errors import NotFoundException
from app.domains.analysis.dependencies import get_analysis_repository
from app.domains.analysis.repository import AnalysisRepository
from app.domains.claims.dependencies import get_claims_service
from app.domains.claims.service import ClaimsService
from app.models.database import User, get_db
from app.schemas.claims import (
    ClaimExtractionRequest,
    ClaimExtractionResult,
    ExtractionMethod,
)
from app.services import claim_export

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("/extract", response_model=ClaimExtractionResult)
async def extract_claims(
    request: ClaimExtractionRequest,
    user: User = Depends(get_current_user),
    service: ClaimsService = Depends(get_claims_service),
) -> ClaimExtractionResult:
    """Extract verifiable advertising claims from raw multimodal signals."""
    return await service.extract(request, plan=user.plan)


@router.post("/from-analysis/{task_id}", response_model=ClaimExtractionResult)
async def extract_claims_from_analysis(
    task_id: str,
    method: ExtractionMethod = Query(
        ExtractionMethod.RULE_BASED, description="Extraction strategy."
    ),
    persist: bool = Query(True, description="Persist the result onto the analysis."),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    repository: AnalysisRepository = Depends(get_analysis_repository),
    service: ClaimsService = Depends(get_claims_service),
) -> ClaimExtractionResult:
    """Extract claims from the signals stored on a finished analysis."""
    analysis = await repository.get_by_task_id(db, task_id, user_id=user.id)
    if analysis is None:
        raise NotFoundException(f"Task {task_id} not found")
    return await service.extract_from_analysis(
        analysis=analysis,
        session=db,
        method=method,
        persist=persist,
        plan=user.plan,
    )


@router.get("/{task_id}", response_model=ClaimExtractionResult)
async def get_claims(
    task_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    repository: AnalysisRepository = Depends(get_analysis_repository),
    service: ClaimsService = Depends(get_claims_service),
) -> ClaimExtractionResult:
    """Return previously persisted claims for an analysis (404 if none yet)."""
    analysis = await repository.get_by_task_id(db, task_id, user_id=user.id)
    if analysis is None:
        raise NotFoundException(f"Task {task_id} not found")
    stored = service.stored_claims(analysis)
    if not stored:
        raise NotFoundException(f"No claims extracted for task {task_id}")
    return ClaimExtractionResult.model_validate(stored)


@router.get("/{task_id}/export")
async def export_claims(
    task_id: str,
    fmt: str = Query("jsonl", alias="format", pattern="^(jsonl|csv)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    repository: AnalysisRepository = Depends(get_analysis_repository),
    service: ClaimsService = Depends(get_claims_service),
) -> Response:
    """Download claims for an analysis as JSONL or CSV (dataset schema rows)."""
    analysis = await repository.get_by_task_id(db, task_id, user_id=user.id)
    if analysis is None:
        raise NotFoundException(f"Task {task_id} not found")

    stored = service.stored_claims(analysis)
    if stored:
        result = ClaimExtractionResult.model_validate(stored)
    else:
        # Extract on the fly (without persisting) so export works pre-extraction.
        result = await service.extract_from_analysis(
            analysis=analysis, session=db, persist=False, plan=user.plan
        )

    if fmt == "csv":
        body = claim_export.to_csv(result)
        media_type = "text/csv"
        filename = f"claims_{task_id}.csv"
    else:
        body = claim_export.to_jsonl(result)
        media_type = "application/x-ndjson"
        filename = f"claims_{task_id}.jsonl"

    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
