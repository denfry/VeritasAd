# Скрипт для локального запуска без Docker (Windows PowerShell)

Write-Host "=== VeritasAd Local Startup ===" -ForegroundColor Green

# Проверка Python
Write-Host "Проверка Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Python не установлен!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green

# Проверка зависимостей
Write-Host "`nПроверка зависимостей..." -ForegroundColor Yellow
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "ОШИБКА: backend\requirements.txt не найден!" -ForegroundColor Red
    exit 1
}

# Установка зависимостей
Write-Host "Установка зависимостей Python..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Не удалось установить зависимости!" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Проверка .env
Write-Host "`nПроверка .env файла..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Создание .env файла..." -ForegroundColor Yellow
    @"
DATABASE_URL=postgresql+psycopg2://veritasad:veritasad@localhost:5432/veritasad
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
STORAGE_DIR=./data/raw
API_KEY=dev-key
USE_MINIO=false
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "✓ .env файл создан" -ForegroundColor Green
} else {
    Write-Host "✓ .env файл существует" -ForegroundColor Green
}

# Проверка PostgreSQL
Write-Host "`nПроверка PostgreSQL..." -ForegroundColor Yellow
$pgTest = psql -U veritasad -d veritasad -c "SELECT 1;" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ PostgreSQL не доступен. Убедись, что:" -ForegroundColor Yellow
    Write-Host "  1. PostgreSQL установлен и запущен" -ForegroundColor Yellow
    Write-Host "  2. База данных 'veritasad' создана" -ForegroundColor Yellow
    Write-Host "  3. Пользователь 'veritasad' с паролем 'veritasad' существует" -ForegroundColor Yellow
} else {
    Write-Host "✓ PostgreSQL доступен" -ForegroundColor Green
}

# Проверка Redis
Write-Host "`nПроверка Redis..." -ForegroundColor Yellow
$redisTest = redis-cli ping 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Redis не доступен. Убедись, что Redis запущен" -ForegroundColor Yellow
} else {
    Write-Host "✓ Redis доступен" -ForegroundColor Green
}

# Проверка ffmpeg
Write-Host "`nПроверка ffmpeg..." -ForegroundColor Yellow
$ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ ffmpeg не найден. Установи ffmpeg и добавь в PATH" -ForegroundColor Yellow
} else {
    Write-Host "✓ ffmpeg: $ffmpegVersion" -ForegroundColor Green
}

Write-Host "`n=== Готово к запуску ===" -ForegroundColor Green
Write-Host "`nЗапусти в отдельных терминалах:" -ForegroundColor Cyan
Write-Host "  Терминал 1 (API):" -ForegroundColor Cyan
Write-Host "    cd backend" -ForegroundColor White
Write-Host "    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "`n  Терминал 2 (Worker):" -ForegroundColor Cyan
Write-Host "    cd backend" -ForegroundColor White
Write-Host "    celery -A backend.celery_app.celery_app worker -Q veritasad -l info" -ForegroundColor White

