from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from app.services.video_processor import VideoProcessor
from app.core.dependencies import get_api_key

router = APIRouter()
processor = VideoProcessor()


@router.post("/check")
async def check_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    api_key: str = Depends(get_api_key)
):
    result = await processor.process(file, url)
    return result