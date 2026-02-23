# VeritasAd - Локальный запуск (PowerShell)
# Использование: .\scripts\local-startup.ps1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  VeritasAd - Локальный запуск" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Docker
Write-Host "Проверка Docker..." -NoNewline
try {
    $dockerVersion = docker --version
    Write-Host " ✅ Docker найден" -ForegroundColor Green
} catch {
    Write-Host " ❌ Docker не найден" -ForegroundColor Red
    Write-Host "Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Проверка .env файла
if (Test-Path ".env") {
    Write-Host "✅ .env файл найден" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env файл не найден" -ForegroundColor Yellow
    Write-Host "Создаю .env из .env.local..."
    Copy-Item ".env.local" ".env"
    Write-Host "✅ .env файл создан" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Отредактируйте .env и установите TELEGRAM_BOT_TOKEN (если нужен бот)" -ForegroundColor Yellow
}

Write-Host ""

# Остановка старых контейнеров
Write-Host "Остановка старых контейнеров..." -NoNewline
docker-compose -f docker-compose.local.yml down 2>$null
Write-Host " ✅" -ForegroundColor Green

# Запуск сервисов
Write-Host ""
Write-Host "Запуск сервисов..." -ForegroundColor Cyan

# Проверка TELEGRAM_BOT_TOKEN
$envContent = Get-Content ".env" -Raw
if ($envContent -match "TELEGRAM_BOT_TOKEN=your_bot_token_here" -or $envContent -match "TELEGRAM_BOT_TOKEN=$") {
    Write-Host "⚠️  TELEGRAM_BOT_TOKEN не установлен, запускаю без бота" -ForegroundColor Yellow
    docker-compose -f docker-compose.local.yml up --build -d backend redis celery-worker frontend
} else {
    docker-compose -f docker-compose.local.yml up --build -d
}

Write-Host ""
Write-Host "✅ Сервисы запущены" -ForegroundColor Green

# Проверка здоровья
Write-Host ""
Write-Host "Проверка здоровья сервисов..." -ForegroundColor Cyan

# Backend
Write-Host "  Backend: " -NoNewline
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Работает" -ForegroundColor Green
            break
        }
    } catch {
        if ($i -eq 30) {
            Write-Host "❌ Не отвечает" -ForegroundColor Red
        } else {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
}

# Frontend
Write-Host "  Frontend: " -NoNewline
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Работает" -ForegroundColor Green
            break
        }
    } catch {
        if ($i -eq 30) {
            Write-Host "❌ Не отвечает" -ForegroundColor Red
        } else {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
}

# Redis
Write-Host "  Redis: " -NoNewline
try {
    $redisPing = docker exec veritasad-redis redis-cli ping 2>$null
    if ($redisPing -eq "PONG") {
        Write-Host "✅ Работает" -ForegroundColor Green
    } else {
        Write-Host "❌ Не отвечает" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Не отвечает" -ForegroundColor Red
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Сервисы запущены!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Адреса:" -ForegroundColor Yellow
Write-Host "   Frontend:  http://localhost:3000"
Write-Host "   Backend:   http://localhost:8000"
Write-Host "   API Docs:  http://localhost:8000/docs"
Write-Host ""
Write-Host "📊 Просмотр логов:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.local.yml logs -f"
Write-Host ""
Write-Host "🛑 Остановка:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.local.yml down"
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
