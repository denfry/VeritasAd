from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid
from datetime import datetime
import subprocess
import logging

from app.core.dependencies import get_api_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(exist_ok=True)


@router.post("/video")
async def upload_video(
    file: UploadFile = File(None),
    url: str = Form(None),
    api_key: str = Depends(get_api_key)
):
    if not file and not url:
        raise HTTPException(400, "Нужен файл или URL")

    video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    video_path = RAW_DIR / f"{video_id}.mp4"

    try:
        if file:
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source = "file"
        else:
            cmd = ["yt-dlp", "-o", str(video_path), "--retries", "3", url]
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if result.returncode != 0:
                raise HTTPException(400, f"yt-dlp error: {result.stderr}")
            source = "url"

        # Аннотация
        annotate_cmd = ["python", "../scripts/auto_annotate.py", "--video-path", str(video_path)]
        annotate_result = subprocess.run(annotate_cmd, capture_output=True, text=True)
        if annotate_result.returncode != 0:
            logger.error(f"Annotation failed: {annotate_result.stderr}")
            raise HTTPException(500, "Ошибка обработки видео")

        return JSONResponse({
            "status": "success",
            "video_id": video_id,
            "source": source,
            "message": "Видео обработано и добавлено в датасет"
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(500, str(e))