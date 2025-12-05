@echo off
REM Скрипт для локального запуска без Docker (Windows CMD)

echo === VeritasAd Local Startup ===

REM Проверка Python
echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен!
    pause
    exit /b 1
)
echo ✓ Python установлен

REM Установка зависимостей
echo.
echo Установка зависимостей Python...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)
cd ..

REM Проверка .env
echo.
echo Проверка .env файла...
if not exist .env (
    echo Создание .env файла...
    (
        echo DATABASE_URL=postgresql+psycopg2://veritasad:veritasad@localhost:5432/veritasad
        echo REDIS_URL=redis://localhost:6379/0
        echo CELERY_BROKER_URL=redis://localhost:6379/0
        echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
        echo STORAGE_DIR=./data/raw
        echo API_KEY=dev-key
        echo USE_MINIO=false
    ) > .env
    echo ✓ .env файл создан
) else (
    echo ✓ .env файл существует
)

echo.
echo === Готово к запуску ===
echo.
echo Запусти в отдельных терминалах:
echo   Терминал 1 (API):
echo     cd backend
echo     uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo   Терминал 2 (Worker):
echo     cd backend
echo     celery -A backend.celery_app.celery_app worker -Q veritasad -l info
echo.
pause

