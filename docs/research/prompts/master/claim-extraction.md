---
id: claim-extraction
title: Промпты извлечения проверяемых рекламных утверждений (zero-shot / few-shot)
phase: master
milestone: M2
status: in-review
date: 2026-06-17
author: denfry
related: ["../../datasets/claims/schema.md", "../../roadmaps/master-2.0.md", "../../plans/master/2026-06-17-m2-claim-extraction-implementation.md"]
---

> **Статус: НА РЕВЬЮ.** Артефакт фиксирует системный и few-shot промпты для LLM-извлечения проверяемых рекламных утверждений из мультимодального контента (VeritasAd 2.0, веха M2). Канонический исполняемый текст промпта и few-shot примеры живут в коде — [`backend/app/services/claim_fewshot.py`](../../../../backend/app/services/claim_fewshot.py); этот документ — его исследовательское зеркало и точка версионирования.

## Назначение

Промпт превращает LLM в подсистему извлечения **проверяемых рекламных утверждений**: из мультимодальных сигналов рекламного видео/поста (ASR, OCR, описание, бренды, disclosure-маркеры, CTA, ссылки) модель выделяет отдельные фактические заявления, переписывает каждое в строгую проверяемую (нормализованную) форму, классифицирует по таксономии (роадмап §8) и присваивает уровень риска (§9). Субъективные оценочные фразы помечаются как непроверяемые.

Промпт обслуживает два из трёх baseline-методов извлечения (роадмап §12.1):

- **LLM zero-shot** (`ExtractionMethod.llm_zero_shot`) — только системная инструкция, без примеров;
- **LLM few-shot** (`ExtractionMethod.llm_few_shot`) — системная инструкция плюс набор демонстраций «вход → ожидаемый выход».

Третий метод, `rule_based`, полностью офлайн (ключевые слова и регулярные выражения) и промпт не использует.

## Контекст применения

Промпт собирается функцией `build_messages(signals, *, few_shot)` в [`backend/app/services/claim_fewshot.py`](../../../../backend/app/services/claim_fewshot.py) и подаётся в унифицированный `app.services.llm_service.LLMService.generate_response`. Сервис `app.services.claim_extractor` парсит и валидирует JSON-ответ модели, привязывая `claim_type` / `risk_level` / `source_modality` к каноническим enum'ам схемы [`backend/app/schemas/claims.py`](../../../../backend/app/schemas/claims.py), после чего нормализация типа/риска, скоринг checkworthiness (§10) и агрегаты считаются на стороне Python.

Вызов происходит **on-demand** за feature-флагом `CLAIM_EXTRACTION_ENABLED` (по умолчанию выключен) через эндпоинты домена `app/domains/claims` (см. план реализации M2). В dev-режиме `MOCK_LLM_RESPONSES` подменяет ответ LLM детерминированной заглушкой, поэтому промпт-методы воспроизводимы без реальных ключей; при недоступности LLM extractor откатывается на `rule_based`.

Конвейерный этап (роадмап §7.1): `ASR + OCR + metadata + links + brand signals → Claim Extractor`.

## Вход

В системный промпт инъектируется канонический словарь схемы (синхронизирован с `app.schemas.claims`):

| Плейсхолдер | Источник | Значение |
| --- | --- | --- |
| `claim_type` | `ClaimType` | `quantitative, comparative, superlative, temporal, financial, health_safety, legal_certification, partnership, availability, subjective, non_checkable` |
| `risk_level` | `RiskLevel` | `low, medium, high, critical` |
| `source_modality` | `SourceModality` | `ocr, asr, metadata, link, description` |

Пользовательское сообщение формируется `_format_signals(signals)` из мультимодальных сигналов (поля `ClaimExtractionRequest`); пустые блоки опускаются, при полном отсутствии сигналов подставляется `(сигналы отсутствуют)`:

| Сигнал (ключ `signals`) | Метка в сообщении | Описание |
| --- | --- | --- |
| `transcript` | `ASR (речь):` | Аудиотранскрипт (ASR). |
| `ocr_text` | `OCR (текст на экране):` | Текст с экрана (OCR). |
| `description` | `Описание/метаданные:` | Описание / метаданные источника. |
| `detected_brands` | `Бренды:` | Имена детектированных брендов (`{name, ...}`). |
| `disclosure_markers` | `Disclosure-маркеры:` | Маркеры раскрытия рекламы. |
| `cta_matches` | `CTA-фразы:` | Сопоставленные call-to-action фразы. |
| `commercial_urls` | `Ссылки:` | Коммерческие / трекинговые URL. |

## Выход

Модель обязана вернуть **только** валидный JSON-массив объектов утверждений, без markdown и пояснений. Если проверяемых утверждений нет — пустой массив `[]`.

```json
{
  "raw_text": "исходный фрагмент, как в контенте",
  "normalized_claim": "строгая проверяемая форма (пустая строка для непроверяемых)",
  "claim_type": "один из 11 классов таксономии",
  "risk_level": "low | medium | high | critical",
  "is_checkable": true,
  "source_modality": "ocr | asr | metadata | link | description",
  "brand": "название бренда или null"
}
```

Поля `id`, `timestamp_start` / `timestamp_end`, `checkworthiness_score`, `checkworthiness_bucket`, `evidence_needed` и `features` LLM **не возвращает** — их достраивает `claim_extractor` (привязка к сегментам ASR, скоринг checkworthiness, агрегаты) при сборке итогового `ClaimExtractionResult`.

## Текст промпта

Системный промпт (`SYSTEM_PROMPT`), `{claim_type}` / `{risk_level}` / `{source_modality}` подставляются из enum'ов схемы:

```text
Ты — система извлечения проверяемых рекламных утверждений из мультимодального
контента (VeritasAd 2.0). Тебе дают сигналы анализа рекламного видео/поста:
аудиотранскрипт (ASR), текст с экрана (OCR), описание, бренды, disclosure-маркеры,
CTA-фразы и ссылки.

Задача: выделить отдельные ПРОВЕРЯЕМЫЕ рекламные утверждения и для каждого вернуть
строго проверяемую (нормализованную) форму, тип и уровень риска.

Проверяемое утверждение — это фактическое заявление, истинность которого в принципе
можно установить по внешним источникам (числа, сравнения, обещания результата,
сертификаты, сроки). Субъективные оценки («идеальный выбор», «вам понравится»)
помечай is_checkable=false и типом subjective или non_checkable.

claim_type ∈ {quantitative, comparative, superlative, temporal, financial,
health_safety, legal_certification, partnership, availability, subjective, non_checkable}.
risk_level ∈ {low, medium, high, critical}.
source_modality ∈ {ocr, asr, metadata, link, description}.

Нормализация: убери маркетинговые усилители и срочность, явно укажи субъект и
измеримый параметр, сохрани количественные границы («до 70%» → верхняя граница).

Верни ТОЛЬКО валидный JSON — массив объектов, без markdown и пояснений.
Каждый объект: {"raw_text": str, "normalized_claim": str, "claim_type": str,
"risk_level": str, "is_checkable": bool, "source_modality": str, "brand": str|null}.
Если проверяемых утверждений нет — верни [].
```

Пользовательское сообщение (целевой вход):

```text
Сигналы:

{signals}
```

В режиме few-shot перед целевым сообщением вставляются демонстрации: для каждого примера — пользовательское сообщение `Сигналы:\n\n{input}` и ответ-ассистент с JSON-массивом ожидаемых утверждений.

## Few-shot примеры

Канонический список — `FEW_SHOT_EXAMPLES` в [`backend/app/services/claim_fewshot.py`](../../../../backend/app/services/claim_fewshot.py). Демонстрации покрывают: одиночное количественное утверждение, разбиение фразы на финансовое + сравнительное, отбраковку субъективной фразы и связку partnership / legal_certification / temporal.

```text
Вход:
Скидка до 70% только сегодня по промокоду VERITAS

Выход:
[{"raw_text": "Скидка до 70% только сегодня",
  "normalized_claim": "Скидка на товар достигает 70%",
  "claim_type": "quantitative", "risk_level": "medium",
  "is_checkable": true, "source_modality": "ocr", "brand": null}]
```

```text
Вход:
Наш банк начисляет 16% годовых на остаток — выгоднее, чем у конкурентов

Выход:
[{"raw_text": "начисляет 16% годовых на остаток",
  "normalized_claim": "Годовая ставка на остаток по счёту составляет 16%",
  "claim_type": "financial", "risk_level": "high",
  "is_checkable": true, "source_modality": "asr", "brand": null},
 {"raw_text": "выгоднее, чем у конкурентов",
  "normalized_claim": "Условия по счёту выгоднее, чем у конкурирующих банков",
  "claim_type": "comparative", "risk_level": "medium",
  "is_checkable": true, "source_modality": "asr", "brand": null}]
```

```text
Вход:
Этот крем идеально подойдёт каждому, вам точно понравится!

Выход:
[{"raw_text": "вам точно понравится", "normalized_claim": "",
  "claim_type": "non_checkable", "risk_level": "low",
  "is_checkable": false, "source_modality": "asr", "brand": null}]
```

```text
Вход:
Официальный партнёр чемпионата, сертифицировано по ГОСТ, доставка за 24 часа

Выход:
[{"raw_text": "Официальный партнёр чемпионата",
  "normalized_claim": "Компания является официальным партнёром чемпионата",
  "claim_type": "partnership", "risk_level": "medium",
  "is_checkable": true, "source_modality": "ocr", "brand": null},
 {"raw_text": "сертифицировано по ГОСТ",
  "normalized_claim": "Товар сертифицирован по стандарту ГОСТ",
  "claim_type": "legal_certification", "risk_level": "high",
  "is_checkable": true, "source_modality": "ocr", "brand": null},
 {"raw_text": "доставка за 24 часа",
  "normalized_claim": "Срок доставки товара составляет 24 часа",
  "claim_type": "temporal", "risk_level": "medium",
  "is_checkable": true, "source_modality": "asr", "brand": null}]
```

## Версия и модель

- **Версия:** v1 (первичный артефакт M2). При выпуске новой версии создавайте `claim-extraction-vN.md`, не перезаписывая этот файл (см. соглашение об именовании в [`../README.md`](../README.md)).
- **Модель:** провайдер-агностично через `LLMService`; в dev — `MOCK_LLM_RESPONSES`. Промпт на русском языке, под русскоязычный рекламный контент.
- **Совместимость:** словарь `claim_type` / `risk_level` / `source_modality` должен оставаться синхронным с enum'ами `app.schemas.claims`; при изменении таксономии правьте код, схему датасета и этот артефакт совместно.

## Связанные документы

- Канонический текст и few-shot: [`backend/app/services/claim_fewshot.py`](../../../../backend/app/services/claim_fewshot.py).
- Контракт данных / pydantic-схемы: [`backend/app/schemas/claims.py`](../../../../backend/app/schemas/claims.py).
- Схема датасета (формат JSONL экспорта): [`../../datasets/claims/schema.md`](../../datasets/claims/schema.md).
- Дорожная карта (таксономия §8, риск §9, checkworthiness §10, baseline §12): [`../../roadmaps/master-2.0.md`](../../roadmaps/master-2.0.md).
- План реализации M2: [`../../plans/master/2026-06-17-m2-claim-extraction-implementation.md`](../../plans/master/2026-06-17-m2-claim-extraction-implementation.md).
- Назад к хабу: [../README.md](../README.md)
</content>
</invoke>
