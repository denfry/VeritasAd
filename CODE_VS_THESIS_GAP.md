# План доработок кода под пояснительную записку (ВКР VeritasAd)

Документ фиксирует расхождения между текстом пояснительной записки (`Юрков_ВКР.docx`)
и фактическим кодом проекта `D:\Projects\VeritasAd`, а также конкретные изменения,
которые нужно внести в код, чтобы он соответствовал написанному.

Для каждого пункта указано: **Заявлено** (в записке) → **Сейчас в коде** (с путём к файлу)
→ **Что сделать**.

## Легенда трудоёмкости и риска

- 🟢 малая правка (часы) · 🟡 средняя (дни) · 🔴 крупная (недели / отдельный модуль)
- ⚠️ — важное замечание. Во многих пунктах код **сложнее/современнее** записки
  (Supabase, Yookassa, 2FA, аудит). Там, где доработка кода «назад» нецелесообразна,
  отмечено: **проще скорректировать формулировку в записке** (1–2 предложения), чем менять код.

## Сводная таблица

| № | Область | Расхождение | Труд-ть | Рекомендация |
|---|---------|-------------|---------|--------------|
| 1 | Веса детекторов | 0.40/0.35/0.15/0.10 ↔ 0.22/0.18/0.28/0.14/0.18 | 🟢 | Привести код к весам записки или наоборот |
| 2 | Порог CLIP | 0.30 ↔ 0.05 | 🟢 | Поднять порог в коде |
| 3 | OCR-движок | Tesseract 5 ↔ EasyOCR | 🟡 | Заменить движок или текст записки |
| 4 | Аудио MFCC/KNN | есть ↔ нет (только ключевые слова) | 🔴 | Реализовать MFCC+KNN |
| 5 | Whisper | base ↔ tiny | 🟢 | Сменить дефолт на base |
| 6 | NMS/IoU | NMS по времени ↔ кластеризация по gap | 🟡 | Реализовать temporal NMS |
| 7 | Частота кадров | 0.5 fps ↔ адаптивная 0.5–1.0 | 🟢 | Зафиксировать 0.5 fps |
| 8 | Celery retries | 3 попытки / 60 с ↔ не задано | 🟢 | Добавить autoretry |
| 9 | Кэш облака | Redis TTL 300 ↔ in-memory TTL 3600 | 🟢 | Перенести в Redis, TTL 300 |
| 10 | Схема БД | UUID, JSONB, GIN, logo_embedding ↔ Integer, JSON, нет GIN | 🔴 | Миграции PostgreSQL |
| 11 | Имена таблиц | videos/analysis_results/reports/brands ↔ analyses/custom_brands | 🟡 | Переименование/представления |
| 12 | Аутентификация | свой JWT register/login/refresh, 24ч/30д ↔ Supabase, 30мин/7д | 🔴 | ⚠️ код современнее — см. п.10 |
| 13 | Эндпоинты | /upload, /analyze, /report/{id} ↔ /analyze/check и др. | 🟡 | Добавить алиасы маршрутов |
| 14 | Rate limiting | свои Redis-счётчики ↔ slowapi | 🟢 | ⚠️ функционально эквивалентно |
| 15 | Тарифы | free/pro/enterprise (3) ↔ 5 планов | 🟢 | ⚠️ проще поправить записку |
| 16 | Frontend-стейт | Zustand ↔ Context + React Query | 🟡 | Внедрить Zustand или поправить текст |
| 17 | Тесты | 137 тестов, 92% ↔ ~62 теста, 37% | 🔴 | Дописать тесты |
| 18 | Нагрузка | Locust 100 польз., 0% ошибок ↔ нет | 🟡 | Создать locustfile + прогон |
| 19 | Оценка ML | F1=0.88 на 50 видео/8ч ↔ 4-классовый, acc≈0.73 | 🔴 | Собрать выборку и прогнать оценку |

---

## 1. Веса детекторов в ансамбле 🟢

- **Заявлено:** CLIP = 0.40, AudioAnalyzer = 0.35, OCR = 0.15, Cloud = 0.10 (сумма 1.0).
- **Сейчас в коде:** `backend/app/services/ad_classification.py` (функция `compute_analysis_decision`):
  `visual·0.22 + audio·0.18 + text·0.28 + disclosure·0.14 + link·0.18`.
  Сигналов **пять** (добавлены `disclosure` и `link`), имена и веса другие.
- **Что сделать (вариант А — под записку):** свести к четырём каналам и весам записки:
  ```python
  confidence_score = min(1.0,
      visual_score * 0.40 +   # CLIP
      audio_score  * 0.35 +   # AudioAnalyzer
      text_score   * 0.15 +   # OCR
      cloud_score  * 0.10)    # Cloud
  ```
  При этом `disclosure_score` и `link_score` либо убрать, либо включить в `text_score`.
- **Что сделать (вариант Б — честнее):** оставить 5 сигналов в коде, но в записке (гл. 3.2,
  Введение, Заключение) описать именно пять каналов и реальные веса. ⚠️ Рекомендуется Б —
  пять каналов выглядят сильнее и соответствуют коду.

## 2. Порог косинусного сходства CLIP 🟢

- **Заявлено:** бренд обнаружен при сходстве **> 0.30**.
- **Сейчас в коде:** `backend/app/core/config.py` → `BRAND_DETECTION_THRESHOLD: float = 0.05`;
  применяется в `backend/app/services/video_processor.py` (`self.detection_threshold`).
- **Что сделать:** поднять до `0.30` в `config.py` (и в `.env` → `BRAND_DETECTION_THRESHOLD=0.30`).
  ⚠️ Это снизит число ложных срабатываний, но и recall — после изменения нужно перепроверить
  метрики (см. п. 19).

## 3. OCR-движок: EasyOCR → Tesseract 5 🟡

- **Заявлено:** Tesseract 5 (LSTM), конфигурация `--oem 3 --psm 6`; предобработка CLAHE +
  бинаризация Оцу + Non-Local Means denoising; нечёткое сравнение по расстоянию Левенштейна (> 0.85).
- **Сейчас в коде:** `backend/app/services/brand_ocr.py` использует **EasyOCR** (`['ru','en']`,
  `text_threshold=0.4`, `gpu=False`); сравнение брендов — нормализация + точное/substring
  совпадение (`_normalize`, `match_brand`), **без Левенштейна**, без CLAHE/Оцу/NLM.
- **Что сделать:**
  1. Заменить зависимость: добавить `pytesseract` + системный `tesseract-ocr` (rus+eng)
     в `backend/Dockerfile`; убрать/оставить `easyocr`.
  2. В `brand_ocr.py` реализовать предобработку кадра OpenCV: `cv2.createCLAHE`,
     `cv2.threshold(..., THRESH_OTSU)`, `cv2.fastNlMeansDenoising`.
  3. Вызов `pytesseract.image_to_string(img, lang='rus+eng', config='--oem 3 --psm 6')`.
  4. Нечёткое сравнение через `Levenshtein.ratio` (пакет `python-Levenshtein`), порог 0.85.
- ⚠️ Альтернатива: оставить EasyOCR и описать его в записке — EasyOCR тоже на нейросети и
  поддерживает ru/en; правка записки здесь дешевле и тоже защитима.

## 4. Аудио: добавить MFCC + KNN 🔴

- **Заявлено:** `librosa`, 40 MFCC-коэффициентов, окно 2 с с перекрытием 50%, KNN (k=5)
  для вероятности принадлежности окна к рекламе; транскрипция faster-whisper.
- **Сейчас в коде:** `backend/app/services/audio_analyzer.py` — только транскрипция
  faster-whisper + поиск по словарю ключевых слов (regex), `score = min(1.0, len(detected)*0.15)`.
  **librosa, MFCC, KNN не используются.**
- **Что сделать:**
  1. Добавить зависимость `librosa` (и `scikit-learn` для KNN).
  2. В `audio_analyzer.py` извлекать MFCC: `librosa.feature.mfcc(y, sr=16000, n_mfcc=40)`
     скользящим окном 2 с (hop = 1 с → перекрытие 50%).
  3. Обучить/сохранить `KNeighborsClassifier(n_neighbors=5)` на размеченных окнах
     (реклама/не реклама), сохранить модель в `models/`.
  4. Возвращать вероятность рекламы по окну и агрегировать с текстовым каналом.
- ⚠️ Требует размеченных аудиоданных. Крупная задача; альтернатива — описать в записке
  реальный keyword-подход (он тоже законный метод аудиоанализа).

## 5. Whisper: tiny → base 🟢

- **Заявлено:** faster-whisper, модель размера **base**.
- **Сейчас в коде:** `config.py` → `WHISPER_MODEL = "tiny"` (диапазон tiny…large).
- **Что сделать:** `WHISPER_MODEL: ... = "base"` в `config.py` и `.env` → `WHISPER_MODEL=base`.
  ⚠️ base медленнее и тяжелее tiny — проверить, что укладывается в `CELERY_TASK_TIME_LIMIT` (600 с).

## 6. Агрегация: реализовать temporal NMS 🟡

- **Заявлено:** Non-Maximum Suppression по времени: для пар кандидатов с temporal IoU > 0.5
  оставляется кандидат с наибольшим `w_score`; фильтрация `w_score < 0.40`.
- **Сейчас в коде:** `backend/app/services/video_processor.py` — **временна́я кластеризация**
  по разрыву `gap_threshold = max(sample_step*1.5, 1.0)`; отдельной функции NMS/IoU нет.
- **Что сделать:** добавить функцию (например в новый `backend/app/services/aggregator.py`):
  ```python
  def temporal_iou(a, b):
      inter = max(0, min(a['end'], b['end']) - max(a['start'], b['start']))
      union = max(a['end'], b['end']) - min(a['start'], b['start'])
      return inter / union if union else 0.0

  def nms_temporal(cands, iou_thr=0.5, score_thr=0.40):
      cands = [c for c in cands if c['w_score'] >= score_thr]
      cands.sort(key=lambda x: x['w_score'], reverse=True)
      kept = []
      for c in cands:
          if not any(temporal_iou(c, k) > iou_thr for k in kept):
              kept.append(c)
      return sorted(kept, key=lambda x: x['start'])
  ```
  Подключить вместо/после кластеризации в `video_processor.py`.

## 7. Частота извлечения кадров: зафиксировать 0.5 fps 🟢

- **Заявлено:** извлечение кадров с частотой **0.5 fps** (1 кадр в 2 с).
- **Сейчас в коде:** `video_processor.py` (≈ строки 629–637) — адаптивно: < 120 с → 0.5 fps,
  иначе 1.0 fps; `BRAND_MAX_FRAMES = 100`, `MAX_VIDEO_DURATION = 600`.
- **Что сделать:** зафиксировать `sample_interval = max(1, int(fps * 0.5))` для всех
  длительностей (убрать ветвление), либо в записке указать «адаптивная частота 0.5–1.0 fps»
  (точнее и тоже корректно — ⚠️ предпочтительно поправить записку).

## 8. Celery: автоповтор 3 раза по 60 с 🟢

- **Заявлено:** при исключении задача повторяется до 3 раз с интервалом 60 с
  (`max_retries=3, default_retry_delay=60`).
- **Сейчас в коде:** `backend/app/core/celery.py` — `task_acks_late=True`,
  `task_reject_on_worker_lost=True`, тайм-лимиты 540/600 с; **автоповтор analyze не задан**
  (retries=5/delay=2 есть только у yt-dlp в `video_processor.py`).
- **Что сделать:** в декораторе задачи анализа указать
  `@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, autoretry_for=(Exception,))`.

## 9. Кэш облачных детекторов: Redis, TTL 300 🟢

- **Заявлено:** ответы кэшируются в Redis по ключу `cloud:{frame_hash}` с TTL **300 с**.
- **Сейчас в коде:** `backend/app/services/cloud_brand_detector.py` — in-memory `dict` `_cache`
  с SHA256-ключом; `BRAND_CLOUD_CACHE_TTL_SECONDS = 3600`.
- **Что сделать:** перенести кэш в Redis (`backend/app/core/redis.py`), ключ
  `cloud:{sha256}`, `setex(..., 300, ...)`; `BRAND_CLOUD_CACHE_TTL_SECONDS = 300`.

## 10. Схема БД: UUID, JSONB, GIN, logo_embedding 🔴

- **Заявлено:** PK типа **UUID**; таблица `brands` с полем `logo_embedding FLOAT[]`
  (512-мерный CLIP-вектор) и `aliases TEXT[]`; `analysis_results` с JSONB-полями
  `ad_segments`, `brands_detected`; **GIN-индекс** по `brands_detected`; таблица `reports`.
- **Сейчас в коде:** `backend/app/models/database.py` — PK **Integer**; типы **JSON**
  (не JSONB); поля `aliases` как JSON; **нет** `logo_embedding` (есть `logo_base64`,
  `logo_url`); **GIN-индексов нет**; отдельной таблицы `reports` нет (`report_path` — поле
  в `analyses`). Alembic используется (12 миграций).
- **Что сделать (крупно):**
  1. Перевести типы на PostgreSQL: `from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID`.
  2. Поля результатов → `JSONB`; `aliases` → `ARRAY(Text)`; добавить
     `logo_embedding = Column(ARRAY(Float))` в модель брендов.
  3. PK → `UUID(as_uuid=True), default=uuid4` (затрагивает все FK — крупная миграция).
  4. GIN-индекс: в миграции Alembic
     `op.create_index('ix_brands_detected_gin', 'analyses', ['detected_brands'], postgresql_using='gin')`.
  5. (Опц.) вынести отчёты в отдельную таблицу `reports(id, analysis_id FK, file_path, format, created_at)`.
- ⚠️ Переход PK Integer→UUID — самый дорогой и рискованный пункт (ломает существующие данные,
  все внешние ключи, Supabase-связки). Трезво оценить: возможно, в записке заменить
  «UUID» на «суррогатный целочисленный первичный ключ» (1 правка) — но логотип-эмбеддинг,
  JSONB и GIN стоит реально внедрить, т.к. на них опирается описание ML и оптимизаций.

## 11. Имена таблиц и сущностей 🟡

- **Заявлено:** `users`, `videos`, `brands`, `analysis_results`, `reports`.
- **Сейчас в коде:** `users`, `analyses`, `custom_brands`, `payments`, `user_credits`,
  `credit_transactions`, `audit_logs`. Нет `videos`/`analysis_results`/`reports`.
- **Что сделать:** либо переименовать модели/таблицы (через Alembic) под записку, либо
  в записке привести реальные имена. ⚠️ В коде сущность «видео» и «результат анализа»
  объединены в `analyses` — это осознанная денормализация, её можно так и описать.

## 12. Аутентификация: свой JWT (register/login/refresh) 🔴 ⚠️

- **Заявлено:** собственная JWT-аутентификация: `POST /auth/register`, `/auth/login`,
  `/auth/refresh`; access 24 ч, refresh 30 дней; `python-jose`; пароли — bcrypt (passlib).
- **Сейчас в коде:** аутентификация через **Supabase JWT** (`backend/app/core/dependencies.py`,
  `verify_supabase_token`), PyJWT + python-jose; access **30 мин**, refresh **7 дней**
  (`config.py`); своих эндпоинтов `/auth/register|login|refresh` нет; пароли в БД не хранятся
  (управляет Supabase), API-ключи хэшируются SHA-256; есть 2FA (TOTP).
- **Что сделать (если строго под записку):**
  1. Добавить `backend/app/core/security.py` с `create_access_token`/`create_refresh_token`
     (python-jose, HS256), `ACCESS_TOKEN_EXPIRE_MINUTES=1440`, `REFRESH_TOKEN_EXPIRE_DAYS=30`.
  2. Добавить роутер `auth` с `/auth/register`, `/auth/login`, `/auth/refresh`; хранить
     `hashed_password` (bcrypt через passlib) в модели `User`.
  3. Включить локальную проверку токена в `get_current_user` параллельно с Supabase.
- ⚠️ **Сильная рекомендация:** код здесь *современнее и безопаснее* записки (Supabase + 2FA).
  Откатывать на самописный JWT — это регресс и большой риск. Гораздо лучше **поправить записку**:
  описать аутентификацию по JWT (Bearer, HS256) с провайдером Supabase, access 30 мин /
  refresh 7 дней, плюс 2FA как преимущество. 2–3 правленых абзаца вместо недели работы.

## 13. Эндпоинты REST API 🟡

- **Заявлено:** `POST /api/v1/upload`, `POST /api/v1/analyze` + `GET /api/v1/analyze/{task_id}`,
  `GET /api/v1/analyze/history`, `POST /api/v1/report/{id}/generate`, `GET /api/v1/report/{id}`.
- **Сейчас в коде:** загрузка и анализ объединены в `POST /api/v1/analyze/check` (file или URL);
  статус/результат — `GET /api/v1/analysis/{task_id}/status` и `/result`; история —
  `GET /api/v1/analyze/history`; отчёты — `GET /api/v1/report/{video_id}`,
  `POST /api/v1/report/generate/{video_id}`. Базовый префикс `/api/v1` ✓.
- **Что сделать:** добавить тонкие алиасы-маршруты под имена записки
  (`/api/v1/upload`, `/api/v1/analyze` (POST), `/api/v1/analyze/{task_id}` (GET)),
  делегирующие в существующие обработчики. Дёшево и не ломает текущий фронт.
- ⚠️ Либо синхронизировать приложение В (спецификация OpenAPI) и записку с реальными путями.

## 14. Rate limiting 🟢 ⚠️

- **Заявлено:** Redis-счётчики с TTL, ключ `ratelimit:{user_id}:{date}`, проверка в middleware.
- **Сейчас в коде:** `backend/app/middleware/rate_limit.py` на **slowapi** (Redis backend,
  fallback in-memory), 60/мин; дневные лимиты по тарифам в `dependencies.py`.
- **Что сделать:** функционально эквивалентно. Либо описать в записке slowapi + дневные квоты
  (предпочтительно, ⚠️ правка текста), либо реализовать ручной счётчик с указанным форматом ключа.

## 15. Тарифные планы 🟢 ⚠️

- **Заявлено:** три тарифа — free / pro / enterprise; квоты free = 1/сутки, pro = 50/сутки.
- **Сейчас в коде:** **пять** планов `UserPlan` (free, starter, pro, business, enterprise);
  лимиты free=1, starter=10, pro=50, business=167, enterprise=667 (`config.py`).
- **Что сделать:** проще и честнее **поправить записку** — указать пять тарифов и реальные
  квоты (это богаче и соответствует коду). Либо схлопнуть enum до трёх планов (затронет
  миграции и платежи — не рекомендуется).

## 16. Frontend: состояние через Zustand 🟡

- **Заявлено:** управление состоянием — **Zustand**; запросы — axios с interceptor (401→refresh).
- **Сейчас в коде:** `frontend/package.json` — Next.js 15.1, React 19, Tailwind 4; состояние —
  **React Context API + TanStack React Query**; **Zustand не используется**; есть axios 1.7.9,
  Supabase, recharts, framer-motion, three.js.
- **Что сделать:** либо добавить `zustand` и перенести часть глобального состояния в store
  (например, профиль/токены), либо в записке (гл. 3.3) заменить «Zustand» на
  «React Context API и TanStack React Query». ⚠️ Правка записки здесь намного дешевле.

## 17. Тесты: 137 шт. и покрытие 92% 🔴

- **Заявлено:** 137 модульных тестов, среднее покрытие 92% (порог 85%), модуль агрегации 97%.
- **Сейчас в коде:** ~**62** тест-функции в 10 файлах `backend/tests/`; покрытие **37%**
  (`htmlcov/index.html`, 2005/5425 строк); pytest 8.3.4 + pytest-asyncio + pytest-cov.
  Низкое покрытие у `video_processor.py` (10%), `ad_classification.py` (10%),
  `report_generator.py` (0%), `model_manager.py` (0%).
- **Что сделать:** дописать тесты прежде всего для ключевых модулей: `ad_classification`
  (агрегация, NMS из п.6), `video_processor`, `brand_ocr`, `audio_analyzer`, роутеры API.
  Цель — довести число до ~137 и покрытие до ≥85–92%. Запускать
  `pytest --cov=app --cov-report=html` и сверять процент.
- ⚠️ Объёмная, но самая «защитимая» работа: реальные тесты = реальные цифры в записке.

## 18. Нагрузочное тестирование (Locust) 🟡

- **Заявлено:** Locust, 100 одновременных пользователей, 10 минут; среднее < 48 мс,
  > 500 RPS, 0% ошибок; таблица 4.2.
- **Сейчас в коде:** **Locust отсутствует** (нет `locustfile.py`), нагрузочных сценариев нет.
- **Что сделать:**
  1. Добавить `locust` в dev-зависимости.
  2. Создать `backend/tests/load/locustfile.py` с `HttpUser`: получение токена,
     `GET /api/v1/analyze/history`, `GET /api/v1/analysis/{task_id}/status`.
  3. Прогнать `locust -u 100 -r 10 -t 10m --host http://localhost:8000`,
     сохранить реальный отчёт (RPS, среднее, P99, % ошибок) и подставить в таблицу 4.2.
- ⚠️ Реальные числа почти наверняка будут отличаться от 48 мс / 500 RPS — внести фактические.

## 19. Оценка качества ML: F1 = 0.88 на 50 видео/8 ч 🔴

- **Заявлено:** тестовая выборка 50 видеозаписей (8 часов) с ручной разметкой; бинарная
  детекция рекламных сегментов; Precision 0.91, Recall 0.85, **F1 = 0.88**; прирост ансамбля
  +5–15%; таблица 4.3 и 4.5 (по детекторам).
- **Сейчас в коде/данных:** `data/annotated/auto_dataset_production_seed/training_report_adboost.json`
  — это **4-классовый** классификатор (no_ad / mention / hidden_ad / official) на ~99 коротких
  записях; лучшая accuracy на тесте ≈ **0.733**, F1 по классам: no_ad 0.857, mention 0.8,
  hidden_ad 0.5; модель помечена `not_enabled_by_default`. Бинарной оценки «реклама/не реклама»
  на 50 видео/8 ч нет.
- **Что сделать:**
  1. Собрать выборку из 50 видеозаписей (~8 ч) и вручную разметить временны́е границы рекламы.
  2. Написать скрипт оценки `scripts/evaluate_detection.py`: прогон пайплайна, сопоставление
     предсказанных и эталонных сегментов по temporal IoU, расчёт Precision/Recall/F1
     для каждого детектора и ансамбля.
  3. Подставить **фактические** числа в таблицы 4.3/4.5 и текст гл. 4.5 и Заключения.
- ⚠️ Самый ответственный пункт для защиты. Если получить ровно F1=0.88 не выйдет — внести
  реальный результат и скорректировать формулировки (комиссия проверяет методику и честность,
  а не «красивость» цифры). Текущий 4-классовый результат тоже можно представить как
  дополнительный эксперимент.

---

## Итоговая рекомендация по приоритетам

**Сделать в коде (реально повышает качество и защитимость):**
- п. 2 (порог CLIP), п. 5 (Whisper base), п. 6 (NMS), п. 8 (Celery retries),
  п. 9 (Redis-кэш) — все 🟢/🟡, дают прямое соответствие записке малой ценой;
- п. 17 (тесты) и п. 18 (Locust) — объёмно, но даёт **настоящие** числа;
- п. 19 (оценка ML) — обязательно для честной защиты результатов;
- из п. 10 — внедрить JSONB + GIN + `logo_embedding` (без смены PK на UUID).

**Проще скорректировать записку (код современнее/эквивалентен) — ⚠️ помечено выше:**
- п. 12 (Supabase вместо самописного JWT + 2FA как плюс),
- п. 14 (slowapi), п. 15 (5 тарифов), п. 16 (Context+React Query),
- частично п. 3 (EasyOCR), п. 7 (адаптивный fps), п. 11 (имена таблиц), п. 13 (пути API).

**Самое дорогое/рискованное — взвесить целесообразность:**
- п. 4 (MFCC+KNN), п. 10 (PK→UUID), п. 12 (откат на самописный JWT).
