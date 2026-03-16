#!/bin/bash
set -e

# Выполняем миграции Alembic перед запуском, если не задана переменная SKIP_MIGRATIONS
if [ "$SKIP_MIGRATIONS" != "true" ]; then
    echo "Running Alembic migrations..."
    # Пытаемся запустить миграции с небольшой задержкой/повторами в случае конфликтов таблиц версий
    for i in {1..5}; do
        alembic upgrade head && break || {
            echo "Migration attempt $i failed, retrying in 2s..."
            sleep 2
        }
    done
else
    echo "Skipping migrations as requested..."
fi

# Запускаем основную команду
exec "$@"
