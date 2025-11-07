# backend/routers/analyze.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
import logging
from pathlib import Path
import json
import subprocess
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import asyncio

load_dotenv()

# === Конфигурация Telegram Client API ===
API_ID_STR = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

if not API_ID_STR or not API_HASH:
    raise ValueError("TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть в .env")

try:
    API_ID = int(API_ID_STR)
except ValueError:
    raise ValueError("TELEGRAM_API_ID должен быть целым числом")

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["analyze"])

POSTS_DIR = Path("../data/raw/posts")
POSTS_DIR.mkdir(exist_ok=True, parents=True)

# Глобальный клиент (сессия сохраняется в veritasad_session.session)
client = TelegramClient("veritasad_session", API_ID, API_HASH)


# === Жизненный цикл FastAPI ===
@router.on_event("startup")
async def startup_event():
    """Подключаемся к Telegram при старте сервера."""
    await client.connect()
    # Авторизация только если ещё не авторизованы
    if not await client.is_user_authorized():
        logger.warning("Клиент не авторизован. Запустите вручную для ввода кода.")
        # Можно добавить интерактивный ввод, но в проде — лучше отдельный скрипт
        # await client.start()  # ← раскомментировать при первом запуске


@router.on_event("shutdown")
async def shutdown_event():
    """Корректно отключаемся."""
    disconnect_coro = client.disconnect()
    if asyncio.iscoroutine(disconnect_coro):
        await disconnect_coro


# === Основной эндпоинт ===
@router.post("/post")
async def analyze_post(
    url: str = Form(..., description="URL поста: t.me, youtube.com, instagram.com/reel, tiktok.com")
):
    post_id = f"post_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    platform = _detect_platform(url)
    raw_path = POSTS_DIR / platform / f"{post_id}.json"
    raw_path.parent.mkdir(exist_ok=True, parents=True)

    try:
        metadata = {}

        if platform == "telegram":
            # --- MTProto: получаем пост ---
            chat_username, message_id = _parse_telegram_url(url)

            entity = await client.get_entity(chat_username)
            if isinstance(entity, (list, tuple)):
                entity = entity[0] if entity else None
            if not entity:
                raise HTTPException(400, "Канал не найден или приватный")

            # === Получаем сообщение ===
            messages = await client.get_messages(entity, ids=message_id)
            if not messages or (isinstance(messages, list) and len(messages) == 0):
                raise HTTPException(400, "Пост не найден или удалён")

            # Исправлено: заменена строка "Returning" на корректное присваивание
            msg = messages[0] if isinstance(messages, list) else messages

            # === Формируем человекочитаемое имя чата/канала/пользователя ===
            chat_title: str = "Неизвестный чат"

            if hasattr(entity, "title") and getattr(entity, "title"):
                chat_title = entity.title
            elif hasattr(entity, "first_name"):
                name_parts = [entity.first_name.strip()] if entity.first_name else []
                if hasattr(entity, "last_name") and entity.last_name:
                    name_parts.append(entity.last_name.strip())
                chat_title = " ".join(name_parts) or getattr(entity, "username", f"ID:{entity.id}")
            else:
                chat_title = getattr(entity, "username", None) or f"ID:{getattr(entity, 'id', 'unknown')}"

            chat_title = str(chat_title) if chat_title else "Неизвестный чат"

            metadata = {
                "text": msg.message or "",
                "chat": {
                    "title": chat_title,
                    "username": getattr(entity, "username", None),
                    "id": entity.id
                },
                "message_id": msg.id,
                "views": getattr(msg, "views", None),
                "date": msg.date.isoformat() if msg.date else None,
                "media": {"type": type(msg.media).__name__} if msg.media else None,
                "url": url
            }

        else:
            # --- yt-dlp для YouTube, Instagram, TikTok и др. ---
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                "--skip-download",
                "--retries", "3",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise HTTPException(400, f"yt-dlp ошибка: {result.stderr}")
            metadata = json.loads(result.stdout)

        # === Сохранение сырых данных ===
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # === Авто-аннотация ===
        annotate_cmd = [
            "python", "../scripts/auto_annotate_post.py",
            "--post-json", str(raw_path),
            "--platform", platform
        ]
        annotate_result = subprocess.run(annotate_cmd, capture_output=True, text=True, timeout=120)
        if annotate_result.returncode != 0:
            logger.error(f"Аннотация не удалась: {annotate_result.stderr}")
            raise HTTPException(500, "Ошибка аннотации поста")

        # === Успешный ответ ===
        return JSONResponse({
            "status": "success",
            "post_id": post_id,
            "platform": platform,
            "title": (metadata.get("text") or "")[:100].strip() + "..." if metadata.get("text") else metadata.get("title", "Без заголовка"),
            "uploader": metadata.get("chat", {}).get("title", metadata.get("uploader", "")),
            "view_count": metadata.get("views"),
            "message": "Пост проанализирован и добавлен в датасет"
        })

    except FloodWaitError as e:
        raise HTTPException(429, f"Telegram: слишком много запросов. Подождите {e.seconds} сек.")
    except SessionPasswordNeededError:
        raise HTTPException(401, "Требуется пароль двухфакторной аутентификации. Запустите вручную.")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Внутренняя ошибка: {str(e)}")


# === Вспомогательные функции ===
def _detect_platform(url: str) -> str:
    url = url.lower()
    if "t.me" in url or "telegram.me" in url:
        return "telegram"
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    if "instagram.com" in url:
        return "instagram"
    if "tiktok.com" in url:
        return "tiktok"
    return "other"


def _parse_telegram_url(url: str):
    import re
    match = re.match(r"https?://t\.me/([a-zA-Z0-9_]+)/(\d+)", url)
    if not match:
        raise HTTPException(400, "Неподдерживаемый формат URL Telegram")
    return match.group(1), int(match.group(2))
