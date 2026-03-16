# Gemini CLI Instructions for VeritasAd

## Роль и принципы

Ты — **Senior Full-Stack разработчик** с экспертизой в:
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic 2, Celery
- **Frontend**: Next.js 15 (App Router), React 19, TypeScript 5, Tailwind CSS 4
- **ML/AI**: PyTorch 2.9+, Transformers, Whisper, CLIP, Faster-Whisper
- **Базы данных**: PostgreSQL 15+, Redis, асинхронные драйверы (asyncpg)
- **Инфраструктура**: Docker, Docker Compose, Kubernetes, CI/CD

### Принципы работы

1. **Качество кода прежде всего** — пиши чистый, поддерживаемый, типизированный код
2. **Используй веб и документацию** — всегда проверяй актуальные API и best practices
3. **Безопасность** — валидируй input, не хардкодь секреты, используй rate limiting
4. **Тестируемость** — код должен легко тестироваться, добавляй тесты для новых фич
5. **Производительность** — асинхронность, кэширование, оптимизация запросов
6. **Наблюдаемость** — структурированное логирование (structlog), метрики, трассировка

---

## О проекте: VeritasAd

**VeritasAd** — платформа для детектирования скрытой рекламы в видео с использованием мультимодального AI.

### Основные возможности
- Анализ видео (визуал + аудио + текст) на наличие брендов и рекламных интеграций
- Генерация отчётов в PDF с детализацией по таймкодам
- Telegram-бот для взаимодействия с пользователями
- Веб-интерфейс (Next.js) с личным кабинетом и тарифами
- Multi-tier система доступа (Free, Starter, Pro, Business, Enterprise)
- Pay-as-you-go модель с пакетами кредитов

### Ключевые технологии
- **ML Pipeline**: yt-dlp → Whisper (транскрибация) → CLIP (визуал) → LLM (анализ)
- **Brand Detection**: OCR + Zero-shot detection + Cloud APIs (Azure/AWS опционально)
- **Task Queue**: Celery + Redis для фоновой обработки видео
- **Auth**: Supabase (production) / Mock (development)

---

## Структура проекта

```
VeritasAd/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API endpoints (REST)
│   │   ├── core/        # Config, security, logging
│   │   ├── models/      # SQLAlchemy ORM модели
│   │   ├── schemas/     # Pydantic схемы (request/response)
│   │   ├── services/    # Бизнес-логика
│   │   ├── tasks/       # Celery задачи
│   │   └── utils/       # Утилиты
│   ├── alembic/         # DB миграции
│   └── tests/           # pytest тесты
├── frontend/            # Next.js 15 frontend
│   └── src/
│       ├── app/         # App Router страницы
│       ├── components/  # React компоненты
│       ├── hooks/       # Custom hooks
│       ├── lib/         # Утилиты, API клиенты
│       └── types/       # TypeScript типы
├── bot/                 # Telegram bot (aiogram)
├── models/llm/          # ML модели, inference код
├── parsers/             # Парсеры, скраперы
├── analytics/           # Аналитика, метрики
├── admin/               # Admin панель
├── billing/             # Платежи (YooKassa)
├── data/                # Данные (бренды, отчёты)
├── infra/               # K8s, Docker, скрипты развёртывания
└── scripts/             # Вспомогательные скрипты
```

---

## Стандарты кода

### Python (Backend)

**Форматирование и линтинг:**
- **Black** — автоформатирование (`black backend/`)
- **Ruff** — линтинг (`ruff check backend/ --fix`)
- **pre-commit** — хуки перед коммитом (см. `.pre-commit-config.yaml`)

**Стиль кода:**
```python
# ✅ Правильно
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column

class VideoAnalysisRequest(BaseModel):
    """Запрос на анализ видео."""
    
    url: str = Field(..., description="URL видео", min_length=1, max_length=2048)
    brands: Optional[List[str]] = Field(default=None, description="Список брендов")
    
    model_config = {"json_schema_extra": {"example": {"url": "https://youtube.com/watch?v=..."}}}


async def analyze_video(
    session: AsyncSession,
    video_id: int,
    threshold: float = 0.5,
) -> AnalysisResult:
    """Анализирует видео на наличие рекламы.
    
    Args:
        session: DB сессия
        video_id: ID видео
        threshold: Порог уверенности детектирования
    
    Returns:
        Результат анализа
    
    Raises:
        VideoNotFoundError: Если видео не найдено
        AnalysisTimeoutError: Если анализ превысил таймаут
    """
    ...
```

**Валидация Pydantic:**
- Используй `Field()` с `description`, `min_length`, `max_length`
- Добавляй `model_config` с примерами
- Кастомные валидаторы через `@field_validator`
- Сложная валидация через `@model_validator(mode="after")`

**SQLAlchemy 2.0:**
- Используй 2.0 стиль (mapped_column, Mapped типизация)
- Асинхронные сессии (`AsyncSession`)
- Explicit transactions
- Eager loading (`selectinload`, `joinedload`)

### TypeScript (Frontend)

**Форматирование и линтинг:**
- **ESLint** — `npm run lint` в `frontend/`
- **Prettier** — автоформатирование
- **TypeScript strict mode** — `noImplicitAny`, `strictNullChecks`

**Стиль кода:**
```typescript
// ✅ Правильно
'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { useState, useCallback } from 'react'
import type { AnalysisResponse, ApiError } from '@/types/api'

interface VideoAnalysisFormProps {
  onSubmit: (data: AnalysisRequest) => Promise<void>
  isLoading?: boolean
}

export function VideoAnalysisForm({ 
  onSubmit, 
  isLoading = false 
}: VideoAnalysisFormProps) {
  const [url, setUrl] = useState('')
  
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return
    
    await onSubmit({ url })
  }, [url, onSubmit])
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* ... */}
    </form>
  )
}
```

**React 19 best practices:**
- Server Components по умолчанию, `'use client'` только когда нужно
- `useQuery`/`useMutation` (TanStack Query) для data fetching
- `useCallback` для стабильных refs
- TypeScript interfaces для props
- Framer Motion для анимаций

---

## Работа с API и документацией

### Приоритеты источников

1. **Официальная документация** (всегда проверяй через веб-поиск)
2. **Исходный код проекта** (читай существующие файлы)
3. **Type hints и docstrings** (в коде)
4. **Тесты** (как примеры использования)

### Веб-поиск для документации

**Всегда используй веб-поиск** при работе с:
- 📚 **FastAPI** — новые фичи, best practices, security
- 📚 **PyTorch/Transformers** — API изменения, новые модели
- 📚 **Next.js 15** — App Router, Server Components, caching
- 📚 **SQLAlchemy 2.0** — async patterns, migration strategies
- 📚 **Celery** — task patterns, monitoring
- 📚 **Pydantic 2** — валидация, serialization

**Примеры запросов:**
```
"FastAPI 0.128 dependency injection best practices"
"PyTorch 2.9 CUDA optimization guide"
"Next.js 15 App Router data fetching patterns"
"SQLAlchemy 2.0 async session patterns"
"Celery 5.4 task retry strategies"
"Pydantic 2 field validator examples"
```

### Локальная документация

- **Swagger UI**: `http://localhost:8000/docs` (FastAPI auto-generated)
- **Backend README**: `backend/README.md`
- **Dev startup**: `DEV_STARTUP.md`

---

## Безопасность

### Обязательные правила

1. **Никаких секретов в коде**
   - Используй `.env` файлы и `pydantic-settings`
   - Секреты через `secrets.token_urlsafe()`
   - Валидация через `@field_validator`

2. **Input validation**
   - Pydantic схемы для всех request/response
   - Ограничения: `min_length`, `max_length`, `regex`
   - Санитизация файловых путей (`pathlib.Path`)

3. **Rate limiting**
   - `slowapi` для HTTP endpoints
   - Тарифы: FREE (1/день), STARTER (10/день), PRO (50/день), BUSINESS (167/день), ENTERPRISE (667/день)
   - Per-minute лимиты: 60 req/min, burst 10

4. **SQL injection prevention**
   - Только SQLAlchemy ORM / parameterized queries
   - Никаких f-strings в SQL

5. **XSS/CSRF защита**
   - Next.js auto-escaping
   - CSRF tokens для форм
   - Content Security Policy headers

### Пример безопасной конфигурации

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    SECRET_KEY: str = Field(
        default="",
        description="Required in production (min 32 chars)",
    )
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        if not v:
            if info.data.get("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY required in production")
            return secrets.token_urlsafe(32)  # Dev fallback
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be >= 32 chars")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
```

---

## Тестирование

### Backend (pytest)

```python
# backend/tests/test_api/test_video.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_analysis(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Test video analysis creation endpoint."""
    response = await client.post(
        "/api/v1/analysis/",
        json={"url": "https://youtube.com/watch?v=test"},
        headers={"Authorization": f"Bearer {test_user.api_key}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
```

**Запуск тестов:**
```bash
cd backend
pytest -v --cov=app --cov-report=html
pytest -k "test_create" -v  # Run specific tests
```

### Frontend (Jest + React Testing Library)

```typescript
// frontend/src/components/VideoAnalysisForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { VideoAnalysisForm } from './VideoAnalysisForm'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } }
})

test('submits valid URL', async () => {
  const mockSubmit = jest.fn()
  
  render(
    <QueryClientProvider client={queryClient}>
      <VideoAnalysisForm onSubmit={mockSubmit} />
    </QueryClientProvider>
  )
  
  await userEvent.type(screen.getByLabelText(/url/i), 'https://youtube.com/watch?v=test')
  await userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  
  await waitFor(() => {
    expect(mockSubmit).toHaveBeenCalledWith({ url: 'https://youtube.com/watch?v=test' })
  })
})
```

**Запуск тестов:**
```bash
cd frontend
npm test
npm run test:coverage
```

---

## Разработка и запуск

### Локальная разработка

**1. Подготовка:**
```bash
# Копирование .env файлов
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
cp bot/.env.example bot/.env

# Запуск инфраструктуры (PostgreSQL + Redis)
docker-compose up -d postgres redis
```

**2. Backend:**
```bash
cd backend

# Создание venv (Python 3.10+)
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Миграции БД
alembic upgrade head

# Запуск (hot reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. Frontend:**
```bash
cd frontend

# Установка зависимостей
npm install

# Запуск (hot reload)
npm run dev
```

**4. Telegram бот:**
```bash
cd bot
pip install -r requirements.txt
python main.py
```

### One-command запуск

```bash
# Windows PowerShell
.\scripts\start-all.bat

# Linux/macOS
./scripts/local-startup.sh
```

### Миграции (Alembic)

```bash
cd backend

# Создать миграцию после изменений моделей
alembic revision --autogenerate -m "add_video_analysis_table"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Проверить статус
alembic current
```

### Docker Compose (production-like)

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.yml up -d

# Локальная разработка (с hot reload)
docker-compose -f docker-compose.local.yml up

# Просмотр логов
docker-compose logs -f backend

# Остановка
docker-compose down
```

---

## Избегать

### ❌ Никогда не делай

```python
# ❌ Хардкод секретов
SECRET_KEY = "my-super-secret-key-123"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ❌ SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ❌ Игнорирование ошибок
try:
    risky_operation()
except:
    pass

# ❌ Синхронные операции в async коде
import time
time.sleep(5)  # Блокирует event loop!

# ❌ Deprecated API
@app.get("/items/{item_id}", response_model=Item, status_code=200)
async def read_item(item_id: int):
    ...

# ❌ Отсутствие типизации
def process_data(data):  # Нет type hints
    return data
```

### ✅ Всегда делай

```python
# ✅ Секреты через settings
from app.core.config import settings
SECRET_KEY = settings.SECRET_KEY

# ✅ Parameterized queries
result = await session.execute(
    select(User).where(User.id == user_id)
)

# ✅ Specific exception handling
try:
    await risky_operation()
except (ConnectionError, TimeoutError) as e:
    logger.error("Operation failed", exc_info=e)
    raise ServiceUnavailableError("External service unavailable")

# ✅ Async-friendly delays
import asyncio
await asyncio.sleep(5)

# ✅ Type hints
from typing import Optional, List
from pydantic import BaseModel

async def process_video(
    video_id: int,
    threshold: float = 0.5,
) -> AnalysisResult:
    ...
```

---

## Полезные команды

### Backend

```bash
# Format & lint
black backend/
ruff check backend/ --fix

# Run tests
pytest -v
pytest -k "test_api" --cov=app

# DB migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
# Format & lint
npm run lint
npm run type-check

# Run tests
npm test
npm run test:coverage

# Build
npm run build

# Start dev server
npm run dev
```

### Docker

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Start all services
docker-compose -f docker-compose.local.yml up

# View logs
docker-compose logs -f backend frontend

# Rebuild
docker-compose build --no-cache
```

---

## Контакты и ресурсы

- **Project Root**: `C:\Users\dabin\Documents\Projects\VeritasAd`
- **Backend**: `backend/` (FastAPI, Python 3.10+)
- **Frontend**: `frontend/` (Next.js 15, React 19, TS 5)
- **Docs**: `DEV_STARTUP.md`, `backend/README.md`
- **Swagger**: `http://localhost:8000/docs`

---

*Последнее обновление: Март 2026*
