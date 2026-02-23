@echo off
chcp 65001 >nul
title VeritasAD Frontend

echo ============================================
echo   VeritasAD Frontend (Next.js)
echo ============================================
echo.

REM Проверка наличия node_modules
if not exist "node_modules" (
    echo [ERROR] node_modules не найден!
    echo Запустите: cd frontend ^&^& npm install
    pause
    exit /b 1
)

REM Проверка наличия .env.local
if not exist ".env.local" (
    echo [WARN] Файл .env.local не найден. Копирую из .env.local.example...
    copy .env.local.example .env.local >nul
)

REM Запуск Next.js dev сервера
echo [INFO] Запуск Next.js dev сервера на порту 3000...
echo [INFO] Документация: http://localhost:3000
echo.
echo Для остановки нажмите Ctrl+C
echo ============================================
echo.

npm run dev

echo.
echo ============================================
echo   Frontend остановлен
echo ============================================
echo.
pause
