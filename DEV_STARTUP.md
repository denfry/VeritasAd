# VeritasAd: Инструкция по запуску (Development)

Этот документ содержит команды для быстрого запуска всех компонентов системы в режиме разработки.

## 1. Подготовка окружения

### Настройка переменных окружения
Скопируйте примеры файлов `.env` и настройте их под свои нужды:

```bash
# Корень проекта
cp .env.example .env

# Бэкенд
cp backend/.env.example backend/.env

# Фронтенд
cp frontend/.env.local.example frontend/.env.local

# Телеграм бот
cp bot/.env.example bot/.env
```

## 2. Инфраструктура (База данных и Redis)

Для локальной разработки проще всего запустить зависимости через Docker:

```bash
# Запуск PostgreSQL и Redis
docker-compose up -d postgres redis
```

## 3. Бэкенд (FastAPI)

Рекомендуется использовать виртуальное окружение Python (3.10+):

```bash
cd backend

# Создание и активация окружения
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций базы данных
alembic upgrade head

# Запуск сервера
python -m app.main
```
*Бэкенд будет доступен по адресу: `http://localhost:8000`*
*Документация Swagger: `http://localhost:8000/docs`*

## 4. Фронтенд (Next.js)

Требуется Node.js 18+:

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev
```
*Фронтенд будет доступен по адресу: `http://localhost:3000`*

## 5. Телеграм бот (Aiogram)

```bash
cd bot

# Рекомендуется отдельное venv или использование того же, что для бэкенда
pip install -r requirements.txt

# Запуск бота
python main.py
```

## 6. Вспомогательные скрипты (One-Command Start)

В проекте уже есть готовые скрипты для автоматизации:

### Windows (PowerShell/Batch):
```powershell
# Запуск всего проекта сразу
.\scripts\start-all.bat

# Или по отдельности:
.\scripts\start-backend.bat
.\scripts\start-frontend.bat
.\scripts\start-celery.bat
```

### Linux/macOS (Shell):
```bash
chmod +x scripts/local-startup.sh
./scripts/local-startup.sh
```

---

## Полезные команды

### Очистка логов
```bash
# Удаление всех логов
rm -rf logs/**/*.log
```

### Работа с миграциями (Alembic)
```bash
cd backend
# Создание новой миграции после изменения моделей
alembic revision --autogenerate -m "description"
# Откат последней миграции
alembic downgrade -1
```
