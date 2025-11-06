# backend/routers/train.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/train", tags=["train"])

@router.post("/")
def start_training():
    try:
        # Запуск скрипта обучения
        cmd = ["python", "../scripts/train.py"]
        logger.info(f"Запуск обучения: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 минут

        if result.returncode == 0:
            return JSONResponse({
                "status": "success",
                "message": "Обучение завершено",
                "output": result.stdout
            })
        else:
            error_msg = f"Ошибка обучения: {result.stderr}"
            logger.error(error_msg)
            raise HTTPException(500, error_msg)

    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Обучение заняло слишком много времени (>5 мин)")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise HTTPException(500, f"Ошибка: {str(e)}")
