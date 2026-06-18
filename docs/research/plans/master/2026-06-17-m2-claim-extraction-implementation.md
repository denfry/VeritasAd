---
id: m2-claim-extraction-implementation
title: Реализация Claim Extraction MVP (VeritasAd 2.0, M2)
phase: master
milestone: M2
status: in-review
date: 2026-06-17
author: denfry
related: ["../../roadmaps/master-2.0.md", "../../specs/master/2026-06-16-multimodal-feature-extraction-design.md", "../../datasets/claims/schema.md"]
---

> **Статус: НА РЕВЬЮ.** Исполняемый бриф и протокол реализации модуля извлечения проверяемых рекламных утверждений (Milestone 2 дорожной карты магистратуры). Часть кода уже реализована по этому брифу; документ служит контрактом и точкой сверки.

## Context

VeritasAd 2.0 (магистратура) переводит систему с уровня «обнаружение рекламных признаков» на уровень «извлечение проверяемых рекламных утверждений» (см. [`../../roadmaps/master-2.0.md`](../../roadmaps/master-2.0.md), §2, §7). Конвейер анализа уже производит мультимодальные сигналы: ASR-транскрипт (+ Whisper-сегменты со `start`/`end`), детектированные бренды, disclosure-маркеры, CTA-фразы, коммерческие ссылки, ad-сегменты (temporal NMS). Не хватало слоя, который из этих сигналов выделяет отдельные **проверяемые утверждения**, нормализует их, классифицирует по таксономии (§8), оценивает риск (§9) и checkworthiness (§10), и отдаёт структурированный результат через API/UI и экспорт в JSONL/CSV (формат датасета — [`../../datasets/claims/schema.md`](../../datasets/claims/schema.md)).

**Решения пользователя:** объём = M2 full-stack (backend + API + frontend + тесты, без dataset-инструментов и экспериментов M3/M4); интеграция = on-demand за feature-флагом `CLAIM_EXTRACTION_ENABLED` (выкл по умолчанию), чтобы соблюсти preserve-behavior из `AGENTS.md`.

## Scope

### В объёме

- Pydantic-схемы `Claim` / `ClaimExtractionRequest` / `ClaimExtractionResult` + enum'ы `ClaimType` (11 классов), `RiskLevel` (4), `SourceModality` (5), `ExtractionMethod` (rule_based / llm_zero_shot / llm_few_shot).
- Сервисы: `claim_extractor` (оркестратор), `claim_normalizer`, `claim_classifier`, `checkworthiness_scorer`, `claim_fewshot` (промпты + few-shot), `claim_export` (JSONL/CSV).
- Три baseline-метода извлечения: rule-based (офлайн), LLM zero-shot, LLM few-shot — через unified `llm_service` (учитывает `MOCK_LLM_RESPONSES`).
- Домен `app/domains/claims/` + эндпоинты `POST /api/v1/claims/extract`, `POST /api/v1/claims/from-analysis/{task_id}`, `GET /api/v1/claims/{task_id}`, `GET /api/v1/claims/{task_id}/export`.
- Колонка `analyses.claims` (JSONB/JSON) + Alembic-миграция 015 (аддитивно, обратимо) + SQLite-синхронизация.
- Feature-flagged хук в конвейере (`tasks/video_analysis.py`) + `claims` в сериализации анализа.
- Frontend: компоненты `ClaimsTable` / `ClaimDetailsCard` / `ClaimRiskBadge` / `ClaimTimeline`, секция claims на странице анализа, API-клиент, типы, i18n (ru/en).
- Unit-тесты на все сервисы + интеграционный тест эндпоинта.
- Промпт-артефакты в `docs/research/prompts/master/`, обновление CHANGELOG и decision-log.

### Вне объёма

- Сбор реального корпуса видео/постов и ручная разметка двумя аннотаторами (M3, ручная работа).
- Dataset-инструменты (валидатор JSONL, train/val/test splitter, Cohen's kappa) — M3.
- Эксперименты, ablation, метрики, error analysis (M4).
- Текст диссертации и публикации (M5).
- Включение извлечения claims в конвейер по умолчанию (флаг остаётся выключенным).

## Контракт данных (для frontend и тестов)

`ClaimExtractionResult` (JSON, как отдаёт API и как лежит в `analysis.claims`):

```jsonc
{
  "claims": [
    {
      "id": "claim_001",
      "raw_text": "Скидка до 70% только сегодня",
      "normalized_claim": "Скидка на товар достигает 70%",
      "source_modality": "ocr",          // ocr | asr | metadata | link | description
      "timestamp_start": 12.4,            // number | null
      "timestamp_end": 14.1,              // number | null
      "claim_type": "quantitative",       // см. таксономию (11 классов)
      "is_checkable": true,
      "checkworthiness_score": 0.91,      // 0..1
      "checkworthiness_bucket": "required", // almost_none|low|desirable|required (computed)
      "risk_level": "medium",             // low|medium|high|critical
      "brand": "BrandName",               // string|null
      "evidence_needed": true,
      "features": {"has_numbers": 0.28, "has_time_limit": 0.12}
    }
  ],
  "method": "rule_based",
  "model": null,                          // string|null (LLM model)
  "content_id": "video_001",
  "source_type": "video",
  "source_url": "https://...",
  "stats": {"total": 1, "checkable": 1, "non_checkable": 0,
             "by_type": {"quantitative": 1}, "by_risk": {"medium": 1},
             "mean_checkworthiness": 0.91},
  "total_claims": 1                       // computed
}
```

`ClaimType`: `quantitative, comparative, superlative, temporal, financial, health_safety, legal_certification, partnership, availability, subjective, non_checkable`.

Эндпоинт для UI: `POST /api/v1/claims/from-analysis/{task_id}?method=rule_based&persist=true` (Bearer-auth, как остальные analysis-эндпоинты). Поле `claims` также приходит в `GET /api/v1/analysis/{task_id}/result`, когда уже извлечено.

## Шаги выполнения

1. ✅ Backend-схемы и сервисы (extractor/normalizer/classifier/scorer/fewshot/export).
2. ✅ Домен claims + регистрация роутера в `app/api/v1/router.py`.
3. ✅ Колонка `analyses.claims`, миграция 015, SQLite-синхронизация, сериализаторы анализа.
4. ✅ Feature-flagged хук в конвейере + настройки `CLAIM_EXTRACTION_ENABLED` / `CLAIM_EXTRACTION_METHOD`.
5. ✅ Frontend: компоненты claims, секция на странице анализа, API-клиент, типы, i18n.
6. ✅ Unit-тесты сервисов (55 шт.) + тест доменного сервиса.
7. ✅ Промпт-доки, CHANGELOG, decision-log.
8. ✅ Прогон: `pytest` (146 passed), `tsc --noEmit` (0), `next lint` (0); ruff/mypy по новым файлам чисты (pre-existing долг репозитория не трогали).

## Затрагиваемые файлы

| Путь | Действие |
| --- | --- |
| `backend/app/schemas/claims.py` | создать |
| `backend/app/services/claim_extractor.py` | создать |
| `backend/app/services/claim_normalizer.py` | создать |
| `backend/app/services/claim_classifier.py` | создать |
| `backend/app/services/checkworthiness_scorer.py` | создать |
| `backend/app/services/claim_fewshot.py` | создать |
| `backend/app/services/claim_export.py` | создать |
| `backend/app/domains/claims/{__init__,router,service,dependencies}.py` | создать |
| `backend/alembic/versions/015_add_analysis_claims.py` | создать |
| `backend/app/api/v1/router.py` | изменить |
| `backend/app/core/config.py` | изменить |
| `backend/app/models/database.py` | изменить |
| `backend/app/tasks/video_analysis.py` | изменить |
| `backend/app/domains/analysis/{progress_router,service}.py` | изменить |
| `backend/app/services/llm_service.py` | изменить (mock claims в dev) |
| `backend/tests/unit/services/test_claim_*.py` | создать |
| `frontend/src/components/Claim*.tsx` | создать |
| `frontend/src/app/(app)/analyze/page.tsx` | изменить |
| `frontend/src/lib/api-client.ts`, `src/types/api.ts`, `src/lib/i18n/{ru,en}.ts` | изменить |
| `docs/research/prompts/master/*.md`, `docs/changelog.md`, `docs/decision-log.md` | создать/изменить |

## Риски и rollback

| Риск | Смягчение | Откат |
| --- | --- | --- |
| Извлечение ломает поведение анализа | Хук за флагом `CLAIM_EXTRACTION_ENABLED=false`; try/except никогда не валит таск | Снять флаг / откатить хук-блок |
| Миграция БД необратима | Аддитивная nullable-колонка + `downgrade()` дропает её | `alembic downgrade -1` |
| LLM недоступен / нет ключей | rule_based по умолчанию (офлайн); LLM-методы с fallback на rule_based | — |
| Несоответствие контракта frontend/backend | Контракт зафиксирован в этом файле; типы TS зеркалят схему | Поправить типы по контракту |

## Verification

Источник чек-листов: [../../execution-checklists.md](../../execution-checklists.md)

**PRE-CODE:**

- [x] business goal and constraints clear
- [x] impacted modules identified
- [x] compatibility and rollback assumptions documented
- [x] test strategy defined

**PRE-MERGE:**

- [x] no unrelated changes (uv.lock / tsbuildinfo churn reverted; pre-existing repo lint debt untouched)
- [x] tests and lint/type checks pass (backend 146 passed; frontend tsc + eslint clean)
- [x] docs and changelog updated
- [x] migration and rollback notes included (015 additive/reversible; flag-off rollback)

---

[К хабу исследований](../../README.md)
