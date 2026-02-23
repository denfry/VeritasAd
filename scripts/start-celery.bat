@echo off
chcp 65001 >nul
title VeritasAD Celery Worker

echo ============================================
echo   VeritasAD Celery Worker
echo ============================================
echo.

REM Проверка наличия .venv
if not exist ".venv" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo Запустите: cd backend ^&^& python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Проверка наличия .env
if not exist ".env" (
    echo [WARN] Файл .env не найден. Копирую из .env.example...
    copy .env.example .env >nul
)

REM Активация виртуального окружения
echo [INFO] Активация виртуального окружения...
call .venv\Scripts\activate.bat

REM Проверка наличия Redis
echo [INFO] Проверка подключения к Redis...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis не запущен!
    echo Запустите Redis:
    echo   - Windows: https://github.com/microsoftarchive/redis/releases
    echo   - Или через Docker: docker run -d -p 6379:6379 redis:7-alpine
    pause
    exit /b 1
)

REM Создание директорий для логов
if not exist "..\logs\backend" mkdir "..\logs\backend"
if not exist "..\logs\celery" mkdir "..\logs\celery"

REM Запуск Celery worker
echo [INFO] Запуск Celery worker...
echo [INFO] Логи: ..\logs\celery\celery.log
echo.
echo Для остановки нажмите Ctrl+C
echo ============================================
echo.

REM Для Windows используем solo pool
celery -A app.core.celery.celery_app worker --loglevel=info --concurrency=2 --pool=solo

echo.
echo ============================================
echo   Worker остановлен
echo ============================================
echo.
pause
