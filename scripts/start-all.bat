@echo off
chcp 65001 >nul
title VeritasAD - Запуск всех сервисов

echo ============================================
echo   VeritasAD - Dev Server
echo   Запуск всех сервисов
echo ============================================
echo.

REM Проверка Redis
echo [INFO] Проверка Redis...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis не запущен!
    echo.
    echo Запустите Redis одним из способов:
    echo   1. Через Docker:
    echo      docker run -d -p 6379:6379 --name veritasad-redis redis:7-alpine
    echo.
    echo   2. Скачайте и установите Redis для Windows:
    echo      https://github.com/microsoftarchive/redis/releases
    echo.
    pause
    exit /b 1
)
echo [OK] Redis запущен
echo.

REM Создание директорий для логов
if not exist "logs\backend" mkdir "logs\backend"
if not exist "logs\celery" mkdir "logs\celery"

echo [INFO] Запуск сервисов...
echo.
echo ============================================
echo   Открываются 3 окна:
echo   - Backend (port 8000)
echo   - Celery Worker
echo   - Frontend (port 3000)
echo ============================================
echo.
echo Для остановки всех сервисов запустите: stop-all.bat
echo.
pause

REM Запуск backend
start "VeritasAD Backend" cmd /k "cd backend && scripts\start-backend.bat"
timeout /t 3 >nul

REM Запуск celery
start "VeritasAD Celery" cmd /k "cd backend && scripts\start-celery.bat"
timeout /t 3 >nul

REM Запуск frontend
start "VeritasAD Frontend" cmd /k "cd frontend && scripts\start-frontend.bat"

echo.
echo [OK] Все сервисы запущены!
echo.
echo URL:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - Backend Docs: http://localhost:8000/docs
echo.
echo Логи:
echo   - Backend: logs\backend\app.log
echo   - Celery: logs\celery\celery.log
echo.
echo ============================================
echo   Окна сервисов открыты и работают
echo   Для остановки: scripts\stop-all.bat
echo ============================================
echo.
pause
