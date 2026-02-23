@echo off
chcp 65001 >nul
title VeritasAD - Остановка всех сервисов

echo ============================================
echo   VeritasAD - Остановка сервисов
echo ============================================
echo.

echo [INFO] Остановка процессов...
echo.

REM Остановка Python процессов (backend и celery)
echo [INFO] Остановка Python процессов (backend, celery)...
taskkill /F /FI "WINDOWTITLE eq VeritasAD Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq VeritasAD Celery*" >nul 2>&1
timeout /t 2 >nul

REM Остановка Node.js процессов (frontend)
echo [INFO] Остановка Node.js процессов (frontend)...
taskkill /F /FI "WINDOWTITLE eq VeritasAD Frontend*" >nul 2>&1
timeout /t 2 >nul

REM Альтернативная остановка по имени процесса
echo [INFO] Дополнительная очистка процессов...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq VeritasAD*" >nul 2>&1
taskkill /F /IM node.exe /FI "WINDOWTITLE eq VeritasAD*" >nul 2>&1

echo.
echo [OK] Все сервисы остановлены!
echo.
echo Если какие-то процессы остались, закройте их вручную:
echo   - Закройте окна "VeritasAD Backend"
echo   - Закройте окно "VeritasAD Celery"
echo   - Закройте окно "VeritasAD Frontend"
echo.
pause
