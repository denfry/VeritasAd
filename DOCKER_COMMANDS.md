# VeritasAd: Docker Commands

Полная инструкция по запуску проекта в Docker для development и production режимов.

## 📋 Структура файлов

```
├── docker-compose.yml          # Production конфигурация
├── docker-compose.dev.yml      # Development конфигурация с hot reload
├── docker-compose.local.yml    # Legacy local development (SQLite)
├── .env.dev                    # Environment для development
├── backend/.env.dev            # Backend environment для development
├── frontend/.env.dev           # Frontend environment для development
├── bot/.env.dev                # Bot environment для development
└── DOCKER_COMMANDS.md          # Этот файл
```

---

## 🚀 Development запуск

### Быстрый старт (все сервисы)

```bash
# Запуск всех сервисов в foreground режиме
docker-compose -f docker-compose.dev.yml up --build

# Запуск всех сервисов в background (detached mode)
docker-compose -f docker-compose.dev.yml up -d --build

# Просмотр логов всех сервисов
docker-compose -f docker-compose.dev.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f celery-worker
docker-compose -f docker-compose.dev.yml logs -f bot
```

### Запуск отдельных сервисов

```bash
# Только backend + PostgreSQL + Redis
docker-compose -f docker-compose.dev.yml up -d backend postgres redis

# Только frontend + backend
docker-compose -f docker-compose.dev.yml up -d frontend backend

# Только bot
docker-compose -f docker-compose.dev.yml up -d bot

# Только инфраструктура (PostgreSQL + Redis)
docker-compose -f docker-compose.dev.yml up -d postgres redis
```

### Остановка сервисов

```bash
# Остановка всех сервисов (сохраняя volumes)
docker-compose -f docker-compose.dev.yml down

# Остановка с удалением volumes (полная очистка данных!)
docker-compose -f docker-compose.dev.yml down --volumes

# Остановка конкретного сервиса
docker-compose -f docker-compose.dev.yml stop backend
```

### Пересборка и перезапуск

```bash
# Пересборка и перезапуск одного сервиса
docker-compose -f docker-compose.dev.yml up -d --build backend

# Пересборка всех сервисов
docker-compose -f docker-compose.dev.yml up -d --build

# Принудительная пересборка без кэша
docker-compose -f docker-compose.dev.yml build --no-cache
```

### Доступ к сервисам

| Сервис | URL | Порт |
|--------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| Backend Swagger | http://localhost:8000/docs | 8000 |
| PostgreSQL | localhost | 5432 |
| Redis | localhost | 6379 |

### Подключение к базе данных

```bash
# Подключение к PostgreSQL через psql
docker-compose -f docker-compose.dev.yml exec postgres psql -U veritasad -d veritasad

# Или из хоста (если установлен psql)
psql -h localhost -U veritasad -d veritasad
# Пароль: veritasad123
```

### Redis CLI

```bash
# Подключение к Redis CLI
docker-compose -f docker-compose.dev.yml exec redis redis-cli

# Или из хоста
redis-cli -h localhost -p 6379
```

---

## 🌐 Production запуск

### Подготовка

```bash
# 1. Скопируйте и настройте .env файл
cp .env.example .env

# 2. Заполните .env реальными значениями:
# - POSTGRES_PASSWORD (надёжный пароль)
# - TELEGRAM_BOT_TOKEN
# - NEXT_PUBLIC_SUPABASE_URL (если используется)
# - NEXT_PUBLIC_SUPABASE_ANON_KEY (если используется)

# 3. Настройте backend/.env для production
# - SECRET_KEY (минимум 32 символа)
# - JWT_SECRET_KEY (минимум 64 символа)
# - CORS_ORIGINS (ваши домены)
# - TRUSTED_HOSTS (ваши домены)
```

### Запуск production

```bash
# Запуск всех production сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery-worker
docker-compose logs -f bot
```

### Остановка production

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (ОСТОРОЖНО: удалит все данные!)
docker-compose down --volumes
```

### Health check

```bash
# Проверка статуса всех сервисов
docker-compose ps

# Проверка здоровья backend
curl http://localhost:8000/health

# Проверка здоровья frontend
curl http://localhost:3000
```

---

## 🔧 Полезные команды

### Логи

```bash
# Последние 100 строк логов
docker-compose -f docker-compose.dev.yml logs --tail=100

# Логи за последние 10 минут
docker-compose -f docker-compose.dev.yml logs --since=10m

# Логи с временными метками
docker-compose -f docker-compose.dev.yml logs -t backend
```

### Выполнение команд внутри контейнеров

```bash
# Выполнить команду в backend контейнере
docker-compose -f docker-compose.dev.yml exec backend python -c "print('Hello')"

# Запустить shell в backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Запустить shell в frontend
docker-compose -f docker-compose.dev.yml exec frontend sh

# Выполнить миграции Alembic вручную
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Запустить тесты
docker-compose -f docker-compose.dev.yml exec backend pytest
```

### Мониторинг

```bash
# Статус всех сервисов
docker-compose -f docker-compose.dev.yml ps

# Статус с подробностями
docker-compose -f docker-compose.dev.yml ps -a

# Использование ресурсов
docker stats

# Просмотр переменных окружения в контейнере
docker-compose -f docker-compose.dev.yml exec backend env
```

### Очистка

```bash
# Удалить все остановленные контейнеры
docker container prune

# Удалить все неиспользуемые volumes
docker volume prune

# Удалить все неиспользуемые images
docker image prune

# Полная очистка (контейнеры, volumes, images, build cache)
docker system prune -a --volumes
```

---

## 📊 Архитектура сервисов

### Development (docker-compose.dev.yml)

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │
│  :3000      │     │    :8000    │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Postgres │ │  Redis   │ │  Celery  │
        │  :5432   │ │  :6379   │ │  Worker  │
        └──────────┘ └──────────┘ └──────────┘
                           │
                           ▼
                      ┌──────────┐
                      │   Bot    │
                      └──────────┘
```

### Production (docker-compose.yml)

```
                    ┌─────────────┐
                    │  Frontend   │
                    │  (Next.js)  │
                    └──────┬──────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐
│   Backend   │◀────│   Celery    │
│  (FastAPI)  │     │   Worker    │
└──────┬──────┘     └─────────────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
 ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Postgres │   │  Redis   │   │   Bot    │
 │  :5432   │   │  :6379   │   │(Telegram)│
 └──────────┘   └──────────┘   └──────────┘
```

---

## ⚠️ Troubleshooting

### Backend не запускается

```bash
# Проверить логи
docker-compose -f docker-compose.dev.yml logs backend

# Пересобрать без кэша
docker-compose -f docker-compose.dev.yml build --no-cache backend

# Проверить подключение к базе
docker-compose -f docker-compose.dev.yml exec backend \
  python -c "from app.core.database import get_db; print('OK')"
```

### Frontend не видит backend

Проверьте `NEXT_PUBLIC_API_URL` в `frontend/.env.dev`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Celery worker не подключается

Проверьте Redis:
```bash
docker-compose -f docker-compose.dev.yml exec redis redis-cli ping
# Должен вернуть: PONG
```

### PostgreSQL не запускается

```bash
# Проверить логи
docker-compose -f docker-compose.dev.yml logs postgres

# Удалить volume и пересоздать (ВНИМАНИЕ: потеря данных!)
docker-compose -f docker-compose.dev.yml down --volumes
docker-compose -f docker-compose.dev.yml up -d postgres
```

### Миграции не применяются

```bash
# Применить миграции вручную
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Проверить статус миграций
docker-compose -f docker-compose.dev.yml exec backend alembic current
```

---

## 📝 Переменные окружения

### Минимальный набор для development

**.env.dev** (корень проекта):
```bash
POSTGRES_PASSWORD=veritasad123
TELEGRAM_BOT_TOKEN=your_token_here
DISABLE_AUTH=true
```

**backend/.env.dev**:
```bash
DATABASE_URL=postgresql+asyncpg://veritasad:veritasad123@postgres:5432/veritasad
REDIS_URL=redis://redis:6379/0
SECRET_KEY=dev-secret-key-min-32-chars
JWT_SECRET_KEY=dev-jwt-secret-key-min-64-chars-long-enough
DISABLE_AUTH=true
```

**frontend/.env.dev**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DISABLE_AUTH=true
```

**bot/.env.dev**:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
API_URL=http://backend:8000
REDIS_URL=redis://redis:6379/2
```

---

## 🎯 Быстрая справка

```bash
# Development - старт
docker-compose -f docker-compose.dev.yml up -d --build

# Development - стоп
docker-compose -f docker-compose.dev.yml down

# Production - старт
docker-compose up -d

# Production - стоп
docker-compose down

# Логи
docker-compose -f docker-compose.dev.yml logs -f [service_name]

# Статус
docker-compose -f docker-compose.dev.yml ps

# Shell в контейнере
docker-compose -f docker-compose.dev.yml exec [service_name] bash
```
