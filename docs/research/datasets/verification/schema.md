---
id: verification-dataset-schema
title: Схема датасета доказательной верификации
phase: phd
milestone: M1
status: draft
date: 2026-06-16
author: (placeholder)
related: ["./annotation-guidelines.md", "../../roadmaps/phd-3.0.md"]
---

> **Статус: ЧЕРНОВИК.** Описание JSONL-схем для claims, evidence и verdicts в датасете доказательной верификации VeritasAd 3.0 (PhD-трек, M1).

## Назначение

Документ фиксирует схемы данных формата JSONL для трёх ключевых сущностей датасета доказательной верификации: утверждений (`claims`), свидетельств (`evidence`) и эталонных вердиктов (`verdicts`). Схемы определяют, как рекламные утверждения извлекаются, сопоставляются с найденными свидетельствами и получают финальную доказательную оценку. Единый формат гарантирует воспроизводимость экспериментов, согласованность разметки между разметчиками и совместимость с пайплайнами обучения и оценки моделей верификации.

## Структура каталога данных

```text
data/datasets/verification/
  claims/      (claims_train.jsonl, claims_val.jsonl, claims_test.jsonl)
  evidence/    (evidence_candidates.jsonl, evidence_ranked.jsonl)
  annotations/ (evidence_relations.jsonl, source_credibility.jsonl, verdicts.jsonl)
  experiments/ (baseline_results.json, ablation_results.json)
  README.md
```

Сами данные — в [../../../../data/datasets/verification/README.md](../../../../data/datasets/verification/README.md).

## Формальная модель

```text
claim c            = {text, normalized_text, type, domain, timestamp, source_modality, risk_level}
evidence item e    = {source, text_span, url, date, source_type, relevance, credibility, freshness, independence, relation}
evidence base E(c) = {e1, e2, ..., en}
relation r(e, c)   in {supports, refutes, partially_supports, partially_refutes, neutral, insufficient}
source credibility = f(authority, primary_source, domain_reputation, transparency, expertise, independence, history, citation_quality)
evidence weight    w(e, c) = alpha*relevance + beta*credibility + gamma*freshness + delta*independence + epsilon*specificity
```

Утверждение `c` нормализуется и типизируется, после чего для него собирается база свидетельств `E(c)`. Каждое свидетельство `e` связано с утверждением отношением `r(e, c)` и получает вес `w(e, c)`, агрегирующий релевантность, достоверность источника, свежесть, независимость и конкретность. Итоговый вердикт по утверждению выводится из взвешенной агрегации отношений по всей базе `E(c)`.

## Формат claim

```json
{
  "claim_id": "claim_001",
  "claim": "Скидка на товар достигает 70%",
  "claim_type": "quantitative",
  "domain": "advertising",
  "risk_level": "medium",
  "source_content_id": "video_001"
}
```

## Формат evidence

```json
{
  "evidence_id": "evidence_001",
  "claim_id": "claim_001",
  "url": "https://example.com/promo",
  "source_title": "Условия акции",
  "source_type": "official",
  "publication_date": "2026-01-15",
  "retrieved_at": "2026-02-01",
  "evidence_span": "Скидка до 70% действует только на отдельные товары...",
  "relation": "partially_supports",
  "relevance_score": 0.91,
  "credibility_score": 0.86,
  "freshness_score": 0.78,
  "annotator_id": "ann_01"
}
```

## Формат вердикта

```json
{
  "claim_id": "claim_001",
  "gold_verdict": "partially_supported",
  "confidence": 0.82,
  "rationale": "Официальный источник подтверждает наличие скидки до 70%, но только для части товаров."
}
```

## Описание полей

Поля записи `claim`:

| Поле | Тип | Описание |
| --- | --- | --- |
| `claim_id` | string | Уникальный идентификатор утверждения. |
| `claim` | string | Текст рекламного утверждения в исходной формулировке. |
| `claim_type` | string | Тип утверждения (например, `quantitative`, `qualitative`, `comparative`). |
| `domain` | string | Предметная область утверждения (например, `advertising`). |
| `risk_level` | string | Уровень риска вводящего в заблуждение утверждения (`low`, `medium`, `high`). |
| `source_content_id` | string | Идентификатор исходного контента, из которого извлечено утверждение. |

Поля записи `evidence`:

| Поле | Тип | Описание |
| --- | --- | --- |
| `evidence_id` | string | Уникальный идентификатор свидетельства. |
| `claim_id` | string | Идентификатор утверждения, к которому относится свидетельство. |
| `url` | string | URL источника свидетельства. |
| `source_title` | string | Заголовок источника. |
| `source_type` | string | Тип источника (например, `official`, `media`, `ugc`). |
| `publication_date` | string | Дата публикации источника (YYYY-MM-DD). |
| `retrieved_at` | string | Дата извлечения свидетельства (YYYY-MM-DD). |
| `evidence_span` | string | Текстовый фрагмент источника, релевантный утверждению. |
| `relation` | string | Отношение свидетельства к утверждению (см. формальную модель). |
| `relevance_score` | float | Оценка релевантности свидетельства утверждению (0–1). |
| `credibility_score` | float | Оценка достоверности источника (0–1). |
| `freshness_score` | float | Оценка свежести свидетельства (0–1). |
| `annotator_id` | string | Идентификатор разметчика, выполнившего разметку свидетельства. |

Поля записи `verdict`:

| Поле | Тип | Описание |
| --- | --- | --- |
| `claim_id` | string | Идентификатор утверждения, к которому относится вердикт. |
| `gold_verdict` | string | Эталонный класс вердикта (см. раздел «Классы вердиктов»). |
| `confidence` | float | Уверенность в эталонном вердикте (0–1). |
| `rationale` | string | Текстовое обоснование вердикта на основе базы свидетельств. |

## Классы вердиктов

| Вердикт | Описание |
| --- | --- |
| `supported` | подтверждается надёжной базой |
| `likely_supported` | большинство надёжных свидетельств поддерживает |
| `partially_supported` | часть подтверждается, часть требует уточнения |
| `conflicting` | база противоречива |
| `not_enough_evidence` | недостаточно свидетельств |
| `likely_refuted` | большинство надёжных свидетельств опровергает |
| `refuted` | явно опровергается надёжными источниками |

## Целевой объём

- 1000–3000 claims;
- 5000–15000 evidence candidates;
- 3–7 evidence на claim;
- 2–3 разметчика.

## Связанные документы

- [./annotation-guidelines.md](./annotation-guidelines.md)
- [../../roadmaps/phd-3.0.md](../../roadmaps/phd-3.0.md) (§8–§12)
