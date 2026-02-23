@echo off
chcp 65001 >nul
title VeritasAD Backend

echo ============================================
echo   VeritasAD Backend Server
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
    echo [WARN] Redis не запущен! Установите и запустите Redis:
    echo   - Windows: https://github.com/microsoftarchive/redis/releases
    echo   - Или через Docker: docker run -d -p 6379:6379 redis:7-alpine
    echo.
    echo Продолжение без Redis может вызвать ошибки...
    echo.
)

REM Создание директорий для логов
if not exist "..\logs\backend" mkdir "..\logs\backend"
if not exist "..\logs\celery" mkdir "..\logs\celery"

REM Запуск сервера
echo [INFO] Запуск backend сервера на порту 8000...
echo [INFO] Логи: ..\logs\backend\app.log
echo [INFO] Документация: http://localhost:8000/docs
echo.
echo Для остановки нажмите Ctrl+C
echo ============================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ============================================
echo   Сервер остановлен
echo ============================================
echo.
pause
