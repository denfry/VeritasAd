# 🎯 VeritasAd — Универсальная система нейросетевого анализа рекламы

> **Дипломный проект + Базис для коммерческого стартапа**
> Мультимодальный анализ рекламных артефактов: видео, посты, сторис, баннеры
> Платформы: **Telegram · VK · Instagram · YouTube · TikTok**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flutter 3.24+](https://img.shields.io/badge/Flutter-3.24+-blue.svg)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-blue.svg)](https://www.docker.com/)

---

## 📦 Структура репозитория

```
veritasad/
├───.github
│   └───workflows
├───admin
│   ├───static
│   │   ├───css
│   │   └───js
│   └───templates
├───analytics
│   └───reports
├───backend
│   ├───routers
│   ├───schemas
│   ├───tests
│   └───utils
├───billing
├───bot
│   ├───handlers
│   └───middlewares
├───data
│   ├───annotated
│   ├───processed
│   ├───raw
│   └───samples
├───docs
│   ├───experiment
│   ├───images
│   ├───presentation
│   └───thesis
│       ├───appendices
│       │   ├───code_samples
│       │   └───reports
│       └───images
├───frontend
│   ├───assets
│   ├───lib
│   │   ├───screens
│   │   ├───services
│   │   ├───theme
│   │   ├───utils
│   │   └───widgets
│   └───platform
│       ├───android
│       ├───ios
│       ├───web
│       └───windows
├───infra
│   ├───ansible
│   ├───docker
│   ├───nginx
│   ├───supervisor
│   └───terraform
├───models
│   ├───audio
│   ├───export
│   ├───llm
│   │   ├───llama-winline-lora
│   │   └───tokenizer
│   ├───ondevice
│   └───vision
├───parsers
│   └───utils
├───scripts
└───setup
```

---

## 🚀 Быстрый старт

### 🔧 Требования
- Python **3.11+**
- Flutter **3.24+**
- Docker + Docker Compose
- Git

### 🪄 Шаг 1. Клонирование
```bash
git clone https://github.com/denfry/VeritasAd.git
cd VeritasAd
```

### 🧩 Шаг 2. Установка зависимостей (локально, если без Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt

# Flutter App
cd ../frontend
flutter pub get
```

### 🐳 Шаг 3. Запуск через Docker (этап 1)

**Важно**: В новых версиях Docker используется `docker compose` (без дефиса), а не `docker-compose`

```bash
# в корне репозитория
docker compose up -d --build
```

**Если Docker не установлен или не распознаётся**, см. [SETUP.md](SETUP.md) для инструкций по установке Docker или локальному запуску без Docker.

Сервисы:
- **API Docs (Swagger)** → http://localhost:8000/docs
- **Redis** → localhost:6379
- **Postgres** → localhost:5432 (user/pass/db: veritasad/veritasad/veritasad)
- **MinIO** → http://localhost:9000 (console http://localhost:9001)

### 🔄 Миграции (Alembic)
```bash
# из корня (использует alembic.ini и DATABASE_URL)
alembic upgrade head
alembic revision --autogenerate -m "comment here"
```

### 🔐 Авторизация (MVP)
- Все защищённые эндпоинты требуют заголовок `X-API-Key`.
- По умолчанию ключ `dev-key`, можно задать в `.env` переменной `API_KEY`.

### ⬇️ Скачивание и метаданные (этап 1.1)
- `POST /jobs` принимает `platform` и `url`, ставит задачу в очередь.
- Celery-воркер собирает метаданные через `yt-dlp --dump-json`, скачивает файл в `data/raw/media/{job_id}.*`, сохраняет мету в `data/raw/meta/{job_id}.json`.
- Извлекает до 10 кадров (`ffmpeg`) в `data/raw/frames/{job_id}/frame_XXX.jpg`, список путей в метаданных (`frames`).
- Извлекает аудио в `data/raw/audio/{job_id}.wav` (16k mono), путь в метаданных (`audio_path`).
- Транскрибирует аудио (whisper tiny) и добавляет `transcript` + простую эвристику `analysis` (label/score/reason).
- При включённом MinIO (`USE_MINIO=true`) загружает артефакты в bucket `veritasad`, добавляет `media_url`/`result_url` в метаданные.
- `GET /jobs/{id}` возвращает статус и пути к результатам (`result_path`, `media_path`, `media_url`, `result_url`).


---

## 🧠 Архитектура MVP

![Архитектура системы](docs/architecture.png)
*См. `docs/architecture.png` — сгенерированная диаграмма компонентов*

### ⚙️ Технологический стек

| Компонент       | Технология                  | Версия       |
|-----------------|-----------------------------|--------------|
| Frontend        | Flutter                     | 3.24+        |
| Backend         | FastAPI                     | 0.104+       |
| Очереди         | Celery + Redis              | 5.3+         |
| База данных     | PostgreSQL                  | 15+          |
| LLM             | Llama 3.1 8B + LoRA         | —            |
| Vision          | CLIP + TFLite               | —            |
| Audio           | Whisper-tiny-ru             | —            |

---

## 🔗 API Примеры

```bash
POST /api/v1/analyze
  → Анализ рекламного артефакта

GET /api/v1/report/{id}
  → Получение PDF-отчёта

GET /api/v1/health
  → Проверка состояния системы
```

### Пример Python-запроса
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"url": "https://t.me/winline_promo/12345", "platform": "telegram"}
)
print(response.json())
```

---

## 🤖 ML Компоненты

### 🔍 LLM Fine-tune (Llama 3.1 8B)
**Назначение:** определение признаков рекламы в тексте
**Метрики:**
- F1-score: **0.89**
- Precision: **0.91**
- Recall: **0.87**

```bash
cd models
python train_llama_lora.py --config model_config.yaml
```

### 🧩 On-device модели
- **CLIP** — визуальные элементы и логотипы
- **MediaPipe** — детекция лиц/эмоций
- **Whisper-tiny-ru** — транскрипция аудио

---

## 📊 Датасет

| Тип артефакта   | Кол-во | Источник             |
|-----------------|--------|----------------------|
| Видео           | 200    | YouTube              |
| Посты           | 500    | Telegram             |
| Изображения     | 300    | Instagram            |
| Stories         | 100    | VK / Instagram       |
| **Итого**       | **1100** | —                  |

### Сбор данных
```bash
python data/telegram_parser.py --channel @winline_promo --limit 500
python data/vk_parser.py --group winline --limit 300
```

### Аннотация
```bash
docker run -p 8080:8080 heartexlabs/label-studio
```

---

## 💼 Коммерческая перспектива

### Бизнес-модель

| Тариф       | Цена/мес     | Анализов | Особенности                     |
|-------------|--------------|----------|---------------------------------|
| Free        | 0 ₽          | 10       | Базовый функционал              |
| Pro         | 15,000 ₽     | 1,000    | API + PDF отчёты                |
| Enterprise  | от 100,000 ₽ | Без ограничений | On-premise, SLA, поддержка |

### Потенциальные клиенты
- Рекламные агентства
- Букмекерские компании
- Маркетинговые отделы брендов
- Блогеры и инфлюенсеры

---

## 🧭 Roadmap

| Период       | Цели |
|--------------|------|
| **2026 Q2**  | Защита диплома: датасет (1100), LLM (F1 > 0.85), MVP |
| **2026 Q3–Q4**| SaaS MVP: пилот с Winline, 100+ клиентов, MRR: 3 млн ₽ |

---

## 🎨 Брендинг

- **Логотип** → `design/logo_veritasad.svg`
- **Гайдлайн** → `design/brand_guidelines.pdf`
- **Figma-макеты** → `design/ui_mockups.fig`

**Цвета:**
- Indigo: `#4F46E5`
- Cyan: `#06B6D4`

**Шрифт:** Inter (Google Fonts)

---

## 📚 Документация

- [`docs/user_guide.md`](docs/user_guide.md) — Руководство пользователя
- [`docs/developer_guide.md`](docs/developer_guide.md) — Для разработчиков
- [`docs/deployment.md`](docs/deployment.md) — Развёртывание

---

## 🧪 Тестирование

```bash
# Unit-тесты backend
pytest tests/ --cov=.

# Flutter-тесты
flutter test
```

---

## 🤝 Контрибуция

1. Сделай **fork**
2. Создай ветку: `git checkout -b feature/amazing`
3. Commit: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing`
5. Создай **Pull Request**

---

## 📄 Лицензия

- **Код:** [MIT License](LICENSE)
- **Датасет:** [CC BY 4.0](data/LICENSE)
- **Диплом:** All Rights Reserved

---

## 📬 Контакты

- **Email:** dabinayo@pm.me
- **Telegram:** [@kfcbossalbino](https://t.me/kfcbossalbino)
- **GitHub:** [denfry](https://github.com/denfry)
- **Website:** [veritasad.ai](https://veritasad.ai)

---

> **VeritasAd — истина в рекламе** 🎯
> ⭐ *Если проект был полезен — поставь звезду на GitHub!*
