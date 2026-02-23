#!/bin/bash
# VeritasAd - Локальный запуск
# Использование: ./scripts/local-startup.sh

set -e

echo "========================================="
echo "  VeritasAd - Локальный запуск"
echo "========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker не установлен${NC}"
        echo "Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose не установлен${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker и Docker Compose найдены${NC}"
}

# Проверка .env файла
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env файл не найден${NC}"
        echo "Создаю .env из .env.local..."
        cp .env.local .env
        echo -e "${GREEN}✅ .env файл создан${NC}"
        echo ""
        echo -e "${YELLOW}📝 Отредактируйте .env файл и установите:${NC}"
        echo "   - TELEGRAM_BOT_TOKEN (если нужен бот)"
        echo ""
        read -p "Продолжить? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✅ .env файл найден${NC}"
    fi
}

# Остановка старых контейнеров
stop_old_containers() {
    echo "Останавливаю старые контейнеры..."
    docker-compose -f docker-compose.local.yml down 2>/dev/null || true
    echo -e "${GREEN}✅ Старые контейнеры остановлены${NC}"
}

# Запуск сервисов
start_services() {
    echo ""
    echo "Запускаю сервисы..."
    echo ""
    
    # Запуск без бота если токен не установлен
    if grep -q "TELEGRAM_BOT_TOKEN=your_bot_token_here" .env 2>/dev/null || \
       grep -q "TELEGRAM_BOT_TOKEN=$" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN не установлен, запускаю без бота${NC}"
        docker-compose -f docker-compose.local.yml up --build -d backend redis celery-worker frontend
    else
        docker-compose -f docker-compose.local.yml up --build -d
    fi
    
    echo ""
    echo -e "${GREEN}✅ Сервисы запущены${NC}"
}

# Проверка здоровья сервисов
check_health() {
    echo ""
    echo "Проверка здоровья сервисов..."
    echo ""
    
    # Проверка backend
    echo -n "  Backend: "
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Работает${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Не отвечает${NC}"
        else
            echo -n "."
            sleep 2
        fi
    done
    
    # Проверка frontend
    echo -n "  Frontend: "
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Работает${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ Не отвечает${NC}"
        else
            echo -n "."
            sleep 2
        fi
    done
    
    # Проверка redis
    echo -n "  Redis: "
    if docker exec veritasad-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✅ Работает${NC}"
    else
        echo -e "${RED}❌ Не отвечает${NC}"
    fi
    
    echo ""
}

# Вывод информации
show_info() {
    echo "========================================="
    echo "  Сервисы запущены!"
    echo "========================================="
    echo ""
    echo "📍 Адреса:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📊 Логи:"
    echo "   docker-compose -f docker-compose.local.yml logs -f"
    echo ""
    echo "🛑 Остановка:"
    echo "   docker-compose -f docker-compose.local.yml down"
    echo ""
    echo "========================================="
}

# Основная функция
main() {
    check_docker
    echo ""
    check_env
    echo ""
    stop_old_containers
    echo ""
    start_services
    echo ""
    check_health
    show_info
}

# Запуск
main
