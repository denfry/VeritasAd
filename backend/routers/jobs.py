from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse

from ..auth import require_api_key
from ..database import session_scope
from ..models import Job, JobStatus
from ..schemas.job import JobResponse
from ..tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(require_api_key)])


@router.post("/", response_model=JobResponse, status_code=202)
def create_job(
    platform: str = Form(..., description="Платформа: telegram|vk|youtube|rutube|twitch"),
    url: str = Form(..., description="Ссылка на контент"),
):
    job = Job(
        platform=platform.lower(),
        input_type="url",
        input_url=url,
        status=JobStatus.PENDING,
    )
    with session_scope() as session:
        session.add(job)
        session.flush()  # get job.id
        job_id = job.id

    # Kick off async processing
    process_job.delay(job_id, url)
    return JSONResponse(
        status_code=202,
        content=JobResponse.model_validate(job).model_dump(),
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    with session_scope() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobResponse.model_validate(job)

