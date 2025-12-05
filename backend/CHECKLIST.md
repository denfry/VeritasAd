# Backend Checklist - Проверка работоспособности

## ✅ Исправлено

1. **Pydantic v2 совместимость**
   - ✅ `from_orm` → `model_validate`
   - ✅ `Config.orm_mode` → `model_config = ConfigDict(from_attributes=True)`
   - ✅ `.dict()` → `.model_dump()`

2. **Зависимости**
   - ✅ `faster-whisper` вместо `openai-whisper` (работает на Windows)
   - ✅ Все пакеты в `requirements.txt`

3. **Функции обновления**
   - ✅ `_update_job` поддерживает `result_url`

4. **Docker**
   - ✅ Dockerfile корректно копирует файлы
   - ✅ docker-compose настроен для всех сервисов

## 🔍 Что проверить при запуске

### 1. Установка зависимостей
```bash
cd backend
pip install -r requirements.txt
```

### 2. Миграции (опционально, если используешь Alembic)
```bash
export DATABASE_URL="postgresql+psycopg2://veritasad:veritasad@localhost:5432/veritasad"
alembic upgrade head
```

### 3. Запуск через Docker
```bash
docker-compose up -d --build
```

### 4. Проверка сервисов
- API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- Redis: localhost:6379
- Postgres: localhost:5432

### 5. Тестовый запрос
```bash
curl -X POST "http://localhost:8000/jobs" \
  -H "X-API-Key: dev-key" \
  -F "platform=youtube" \
  -F "url=https://www.youtube.com/watch?v=..."
```

### 6. Проверка статуса задачи
```bash
curl -X GET "http://localhost:8000/jobs/{job_id}" \
  -H "X-API-Key: dev-key"
```

## ⚠️ Возможные проблемы

1. **Whisper модель**: При первом запуске `faster-whisper` скачает модель "tiny" (~75MB)
2. **MinIO bucket**: Создаётся автоматически при первом использовании
3. **ffmpeg**: Должен быть установлен в Docker-образе (уже есть в Dockerfile)

## 📝 Структура проекта

```
backend/
├── __init__.py
├── main.py              # FastAPI app
├── database.py          # SQLAlchemy setup
├── models.py            # Job model
├── settings.py          # Configuration
├── auth.py              # API key auth
├── celery_app.py        # Celery setup
├── tasks.py             # Celery tasks (download, transcribe, classify)
├── storage.py           # MinIO upload
├── routers/
│   ├── __init__.py
│   ├── jobs.py          # Main API endpoints
│   ├── upload.py        # Legacy (можно удалить)
│   ├── train.py         # Legacy (можно удалить)
│   └── analyze.py       # Legacy (можно удалить)
├── schemas/
│   ├── __init__.py
│   └── job.py           # Pydantic schemas
├── utils/
│   └── platform.py      # Platform detection
└── migrations/          # Alembic migrations
    ├── env.py
    └── versions/
        └── 20241229_0001_create_jobs.py
```

