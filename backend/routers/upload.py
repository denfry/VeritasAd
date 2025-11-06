# backend/routers/upload.py (обновлённая версия)
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import subprocess
import uuid
from datetime import datetime
import logging  # NEW: для отладки

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

RAW_DIR = Path("../data/raw")
ANNOTATED_DIR = Path("../data/annotated/disclosure_dataset")
RAW_DIR.mkdir(exist_ok=True)
ANNOTATED_DIR.mkdir(exist_ok=True)

@router.post("/video")
async def upload_video(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    if not file and not url:
        raise HTTPException(400, "Укажите файл или URL")

    video_id = f"{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    video_path = RAW_DIR / f"{video_id}.mp4"

    try:
        if file:
            with open(video_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            source = "file"
            logger.info(f"Файл загружен: {video_path}")
        else:
            # Улучшенный yt-dlp для Telegram: добавлены опции для лучшей совместимости
            cmd = [
                "yt-dlp",
                "-o", str(video_path),
                "--no-warnings",  # Подавить предупреждения
                "--extractor-retries", "3",  # Повторы
                url
            ]
            if "t.me" in url:
                cmd += ["--cookies-from-browser", "chrome"]  # NEW: cookies для приватных (если браузер Chrome установлен)

            logger.info(f"Запуск yt-dlp: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)  # Timeout 60s
            logger.info(f"yt-dlp stdout: {result.stdout}")
            logger.info(f"yt-dlp stderr: {result.stderr}")

            if result.returncode != 0:
                error_msg = f"Ошибка скачивания: {result.stderr or 'Неизвестная ошибка'} (код: {result.returncode})"
                logger.error(error_msg)
                raise HTTPException(400, error_msg)

            if not video_path.exists() or video_path.stat().st_size == 0:
                raise HTTPException(400, "Скачивание завершилось, но файл пустой или отсутствует")

            source = "url"
            logger.info(f"Видео скачано: {video_path} ({video_path.stat().st_size} байт)")

        # Авто-аннотация (с проверкой)
        annotate_cmd = ["python", "../scripts/auto_annotate.py", "--video-path", str(video_path)]
        annotate_result = subprocess.run(annotate_cmd, capture_output=True, text=True)
        if annotate_result.returncode != 0:
            logger.error(f"Ошибка аннотации: {annotate_result.stderr}")
            raise HTTPException(500, f"Ошибка обработки видео: {annotate_result.stderr}")

        return JSONResponse({
            "status": "success",
            "video_id": video_id,
            "source": source,
            "message": "Видео обработано и добавлено в датасет",
            "file_size": video_path.stat().st_size if video_path.exists() else 0
        })

    except HTTPException:
        raise  # Пробрасываем 400/500 от yt-dlp
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(500, error_msg)
