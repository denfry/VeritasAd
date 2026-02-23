# Логи приложения VeritasAd

В этой директории хранятся лог-файлы приложения.

## Структура

```
logs/
├── backend/
│   └── app.log          # Логи backend приложения
└── celery/
    └── celery.log       # Логи Celery worker
```

## Просмотр логов

### В реальном времени (Linux/Mac)
```bash
# Backend логи
tail -f logs/backend/app.log

# Celery логи
tail -f logs/celery/celery.log

# Оба файла одновременно
tail -f logs/backend/app.log logs/celery/celery.log
```

### В реальном времени (Windows PowerShell)
```powershell
# Backend логи
Get-Content logs\backend\app.log -Wait -Tail 50

# Celery логи
Get-Content logs\celery\celery.log -Wait -Tail 50
```

### Через Docker
```bash
# Логи backend контейнера
docker logs -f veritasad-backend

# Логи celery контейнера
docker logs -f veritasad-celery
```

## Ротация логов

Логи автоматически ротируются при достижении размера 10MB.
Хранится до 5 архивных файлов для каждого лога.

## Уровень логирования

Установите через переменную окружения `LOG_LEVEL`:
- `DEBUG` - полная отладочная информация
- `INFO` - стандартная информация (по умолчанию)
- `WARNING` - только предупреждения и ошибки
- `ERROR` - только ошибки
- `CRITICAL` - только критические ошибки

## Формат логов

Установите через переменную окружения `LOG_FORMAT`:
- `text` - человекочитаемый формат (для разработки)
- `json` - JSON формат (для production и парсинга)
