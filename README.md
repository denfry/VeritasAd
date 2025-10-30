# 🎯 VeritasAd — Универсальная система нейросетевого анализа рекламы

> **Дипломный проект + Коммерческий стартап**  
> Мультимодальный анализ: Видео + Посты + Stories + Баннеры  
> Платформы: Telegram, VK, Instagram, YouTube, TikTok

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flutter 3.24+](https://img.shields.io/badge/flutter-3.24+-blue.svg)](https://flutter.dev/)

---

## 📦 Что внутри репозитория

```
veritasad/
├── diploma/          # 🎓 Дипломные материалы
├── mvp/             # 💻 Рабочий код приложения
├── data/            # 📊 Датасет и скрипты сбора
├── models/          # 🤖 ML-модели и обучение
├── commercial/      # 💼 Бизнес-материалы
├── design/          # 🎨 Брендинг и UI/UX
└── docs/            # 📚 Документация
```

---

## 🚀 Быстрый старт (5 минут)

### Требования
- Python 3.11+
- Flutter 3.24+
- Docker & Docker Compose
- Git

### Шаг 1: Клонирование
```bash
git clone https://github.com/yourusername/veritasad.git
cd veritasad
```

### Шаг 2: Установка зависимостей
```bash
# Python backend
cd mvp/backend
pip install -r requirements.txt

# Flutter app
cd ../flutter_app
flutter pub get
```

### Шаг 3: Запуск через Docker
```bash
cd mvp
docker-compose up -d
```

### Шаг 4: Открой приложение
- **Web**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **Monitoring**: http://localhost:9090

---

## 🎓 Дипломная работа

### Тема
**"Разработка универсальной подсистемы нейросетевого анализа артефактов рекламных интеграций в цифровых медиа"**

### Структура диплома
| Раздел | Страниц | Файл |
|--------|---------|------|
| Введение | 3-5 | `diploma/01_intro.tex` |
| Аналитический обзор | 12-15 | `diploma/02_analysis.tex` |
| Методология | 10-12 | `diploma/03_methodology.tex` |
| Разработка системы | 15-18 | `diploma/04_development.tex` |
| Эксперимент | 8-10 | `diploma/05_experiment.tex` |
| Заключение | 2-3 | `diploma/06_conclusion.tex` |

### Компиляция диплома
```bash
cd diploma
pdflatex thesis.tex
bibtex thesis
pdflatex thesis.tex
pdflatex thesis.tex
```

**Или используй Overleaf**: загрузи папку `diploma/` → автокомпиляция

---

## 💻 MVP Архитектура

### Технологический стек
| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Frontend | Flutter | 3.24+ |
| Backend | FastAPI | 0.104+ |
| Queue | Celery + Redis | 5.3+ |
| Database | PostgreSQL | 15+ |
| LLM | Llama 3.1 8B + LoRA | - |
| Vision | CLIP + TFLite | - |
| Audio | Whisper-tiny-ru | - |

### API Endpoints
```bash
POST /api/v1/analyze
  → Анализ рекламного артефакта

GET /api/v1/report/{id}
  → Получить PDF-отчёт

GET /api/v1/health
  → Проверка здоровья системы
```

### Пример использования API
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "url": "https://t.me/winline_promo/12345",
        "platform": "telegram"
    }
)

result = response.json()
print(f"AdScore: {result['ad_score']}/100")
print(f"Compliance: {result['compliance']['status']}")
```

---

## 🤖 ML Модели

### 1. Fine-tuned LLM (Llama 3.1 8B)
**Задача**: Детекция маркеров рекламы в тексте

**Метрики на тестовой выборке**:
- F1-score: **0.89**
- Precision: **0.91**
- Recall: **0.87**

**Обучение**:
```bash
# Открой Colab ноутбук
models/fine_tune_colab.ipynb

# Или локально (если есть GPU)
cd models
python train_llama_lora.py --config model_config.yaml
```

### 2. On-device модели (TFLite)
- **CLIP**: детекция логотипов и визуальных элементов
- **MediaPipe**: детекция лиц/эмоций
- **Whisper-tiny-ru**: транскрипция аудио

**Конвертация**:
```bash
python models/tflite_conversion.py
```

---

## 📊 Датасет

### Статистика
| Тип артефакта | Количество | Источник |
|---------------|------------|----------|
| Видео | 200 | YouTube (Winline, 1xBet) |
| Посты | 500 | Telegram @winline_promo |
| Изображения | 300 | Instagram #реклама |
| Stories | 100 | VK/Instagram |
| **Итого** | **1100** | - |

### Сбор данных
```bash
cd data/collection_scripts

# Telegram посты
python telegram_parser.py --channel @winline_promo --limit 500

# VK посты
python vk_parser.py --group winline --limit 300

# Instagram (требует cookies)
python instagram_parser.py --hashtag реклама --limit 300
```

### Аннотация
```bash
# Открой Label Studio
docker run -p 8080:8080 heartexlabs/label-studio

# Импортируй data/label_studio_config.json
```

---

## 💼 Коммерциализация

### Бизнес-модель
| План | Цена/мес | Анализов | Фичи |
|------|----------|----------|------|
| **Free** | 0₽ | 10 | Базовый анализ |
| **Pro** | 15,000₽ | 1,000 | API, экспорт PDF |
| **Enterprise** | От 100,000₽ | Unlimited | On-premise, SLA |

### Целевая аудитория
1. **Рекламные агентства** — проверка 1000+ постов/день
2. **Букмекеры/Криптобиржи** — compliance-риски (штрафы до 500 тыс ₽)
3. **Блогеры** — самопроверка интеграций

### Первый клиент (Pilot)
**Winline** — букмекерская компания, 500+ интеграций/месяц

**План**:
1. Бесплатно проверить 100 интеграций (июль 2026)
2. Получить testimonial + кейс
3. Предложить платный план (август 2026)

**Email-шаблон**: `commercial/winline_email_template.docx`

---

## 📈 Roadmap

### 2026 Q2: Диплом
- [x] Сбор датасета (1100 артефактов)
- [x] Fine-tune LLM (F1 > 0.85)
- [x] MVP приложение (Flutter + FastAPI)
- [ ] Защита диплома (июнь 2026)

### 2026 Q3-Q4: Запуск SaaS (СНГ)
- [ ] Pilot с Winline (июль)
- [ ] Публичный запуск (август)
- [ ] 100 платных клиентов (декабрь)
- [ ] MRR: 3 млн ₽

### 2027-2028: Global Expansion
- [ ] EN-версия приложения
- [ ] AWS EU/US регионы
- [ ] Интеграции: TikTok, Twitter/X
- [ ] ARR: $2M

---

## 🎨 Брендинг

### Логотип
- **Файл**: `design/logo_veritasad.svg`
- **Цвета**: 
  - Primary: `#4F46E5` (Indigo)
  - Secondary: `#06B6D4` (Cyan)
- **Шрифт**: Inter (Google Fonts)

### UI/UX
- **Figma**: `design/ui_mockups.fig`
- **Гайдлайн**: `design/brand_guidelines.pdf`

---

## 📚 Документация

- **API Docs**: http://localhost:8000/docs (Swagger)
- **User Guide**: `docs/user_guide.md`
- **Developer Guide**: `docs/developer_guide.md`
- **Deployment Guide**: `docs/deployment.md`

---

## 🧪 Тестирование

```bash
# Backend тесты
cd mvp/backend
pytest tests/ --cov=.

# Flutter тесты
cd mvp/flutter_app
flutter test

# E2E тесты
cd mvp
docker-compose -f docker-compose.test.yml up
```

---

## 🤝 Контрибуция

Проект создан для дипломной работы, но открыт для вклада:

1. Fork репозитория
2. Создай feature branch (`git checkout -b feature/amazing`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing`)
5. Открой Pull Request

---

## 📄 Лицензия

- **Код**: MIT License
- **Датасет**: CC BY 4.0
- **Диплом**: All Rights Reserved

---

## 📧 Контакты

- **Email**: your.email@example.com
- **Telegram**: @yourusername
- **GitHub**: github.com/yourusername
- **Website**: veritasad.ai

---

## ⭐ Если проект полезен

Поставь звезду на GitHub! Это мотивирует развивать проект дальше.

---

**VeritasAd** — *истина в рекламе* 🎯