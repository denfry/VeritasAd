# VeritasAd 3.0 — Roadmap аспирантуры

**Проект:** VeritasAd  
**Уровень:** аспирантура / кандидатская диссертация  
**Базовая линия:** развитие VeritasAd 2.0 после магистратуры  
**Целевой результат:** исследовательская система доказательной верификации проверяемых утверждений в рекламном и цифровом медиаконтенте

---

## 1. Рекомендуемая тема аспирантуры

### Основная формулировка

> **Методы доказательной верификации проверяемых утверждений в рекламном и цифровом медиаконтенте на основе больших языковых моделей и взвешенной оценки внешних свидетельств.**

### Более сильная формулировка

> **Методы доказательной верификации проверяемых утверждений в цифровом медиаконтенте в условиях неполной и противоречивой внешней доказательной базы.**

### Формулировка с акцентом на RAG

> **Методы credibility-aware retrieval-augmented верификации проверяемых утверждений в цифровом медиаконтенте.**

### Формулировка с акцентом на рекламу

> **Методы доказательной верификации рекламных утверждений на основе больших языковых моделей, внешних свидетельств и оценки достоверности источников.**

### Рекомендуемый вариант для утверждения

> **Методы доказательной верификации проверяемых утверждений в цифровом медиаконтенте в условиях неполной и противоречивой внешней доказательной базы.**

Причина выбора: формулировка показывает научную проблему, а не просто применение LLM. Центральный акцент — работа с неполными, противоречивыми и разнонадежными свидетельствами.

---

## 2. Стратегическая идея аспирантуры

Если магистратура закрывает задачу **извлечения проверяемых утверждений**, то аспирантура должна перейти к задаче **доказательной верификации этих утверждений через внешние источники**.

```text
VeritasAd 1.0 — анализ рекламных артефактов
        ↓
VeritasAd 2.0 — извлечение и классификация проверяемых claims
        ↓
VeritasAd 3.0 — доказательная верификация claims
        ↓
VeritasAd Research — методология доверенной проверки цифрового контента
```

Аспирантура должна доказать не то, что LLM можно применить для фактчекинга, а то, что **учет достоверности, независимости, актуальности и противоречивости внешних свидетельств повышает качество автоматизированной верификации утверждений**.

---

## 3. Научное позиционирование

### 3.1. Область исследования

- искусственный интеллект;
- NLP;
- information retrieval;
- retrieval-augmented generation;
- automated fact-checking;
- source credibility assessment;
- contradiction detection;
- evidence aggregation;
- explainable AI;
- trustworthy AI;
- мультимодальный анализ цифрового контента.

### 3.2. Объект исследования

> **Процессы автоматизированной доказательной верификации проверяемых утверждений в цифровом рекламном и медиаконтенте.**

### 3.3. Предмет исследования

> **Модели, методы и алгоритмы поиска, отбора, взвешивания и агрегации внешних свидетельств для формирования объяснимого вердикта по проверяемым утверждениям с учетом достоверности источников и противоречий между свидетельствами.**

### 3.4. Цель исследования

> **Разработать и экспериментально оценить методы доказательной верификации проверяемых утверждений в цифровом медиаконтенте, обеспечивающие поиск внешних свидетельств, оценку достоверности источников, анализ противоречий, агрегацию доказательной базы и формирование калиброванного объяснимого вердикта.**

### 3.5. Гипотеза

> **Если при автоматизированной верификации утверждений использовать не только семантическую релевантность найденных документов, но и формализованную оценку достоверности, независимости, актуальности и противоречивости внешних свидетельств, то качество вердикта, его объяснимость и калибровка уверенности будут выше, чем у стандартных LLM/RAG-подходов.**

---

## 4. Центральная научная проблема

Существующие LLM/RAG-подходы могут находить релевантные документы и генерировать убедительные ответы, но они часто недостаточно надежны в условиях, когда:

- источники противоречат друг другу;
- один источник является рекламным или заинтересованным;
- часть информации устарела;
- найденные документы релевантны семантически, но не являются доказательствами;
- источник авторитетен в одной области, но некомпетентен в другой;
- утверждение требует временной, числовой или контекстной интерпретации;
- отсутствует достаточная доказательная база;
- LLM генерирует чрезмерно уверенный вердикт при слабых свидетельствах.

Научная проблема:

> **Отсутствие формализованных и экспериментально подтвержденных методов доказательной верификации утверждений, которые объединяют поиск внешних свидетельств, оценку достоверности источников, анализ противоречий и калиброванную агрегацию доказательств.**

---

## 5. Ожидаемая научная новизна

1. **Формальная модель доказательной базы** для проверяемого утверждения, включающая внешние свидетельства, источники, веса, релевантность, дату, независимость и отношение к утверждению.
2. **Метод credibility-aware evidence retrieval**, который ранжирует свидетельства не только по семантической близости, но и по достоверности, актуальности и типу источника.
3. **Метод анализа противоречивых свидетельств**, определяющий support/refute/partial/neutral/conflict relations между утверждением и найденными доказательствами.
4. **Алгоритм агрегации доказательной базы**, формирующий калиброванный вердикт с учетом весов источников и конфликтности.
5. **Модель объяснимой верификации**, показывающая пользователю не только вердикт, но и цепочку доказательств.
6. **Экспериментальная методика оценки** устойчивости системы к противоречивым, шумным, устаревшим и недостоверным источникам.
7. **Расширение VeritasAd до исследовательской платформы evidence-based verification.**

---

## 6. Потенциальные положения на защиту

1. Метод формирования доказательной базы проверяемого утверждения, включающий извлечение evidence candidates, их нормализацию, ранжирование и классификацию по отношению к утверждению.
2. Модель взвешенной оценки внешних свидетельств с учетом релевантности, достоверности, актуальности, независимости и типа источника.
3. Алгоритм анализа противоречий между внешними свидетельствами и проверяемым утверждением.
4. Метод агрегации доказательной базы для формирования калиброванного вердикта.
5. Архитектура VeritasAd 3.0 как исследовательской системы доказательной верификации рекламного и цифрового медиаконтента.
6. Экспериментальные результаты, подтверждающие преимущество предложенного подхода над LLM-only и standard RAG baseline.

---

## 7. Архитектура VeritasAd 3.0

### 7.1. Общая схема

```text
Digital Content
        ↓
Ad/Media Analyzer
        ↓
Claim Extraction  ← результат магистратуры
        ↓
Claim Normalization
        ↓
Query Generation
        ↓
Evidence Retrieval
        ↓
Source Credibility Scoring
        ↓
Evidence Relation Classification
        ↓
Contradiction Analysis
        ↓
Evidence Aggregation
        ↓
Calibrated Verdict
        ↓
Explainable Report
```

### 7.2. Рекомендуемые новые backend-модули

```text
backend/app/services/evidence_retriever.py
backend/app/services/query_generator.py
backend/app/services/source_credibility.py
backend/app/services/evidence_ranker.py
backend/app/services/evidence_relation_classifier.py
backend/app/services/contradiction_analyzer.py
backend/app/services/evidence_aggregator.py
backend/app/services/verdict_generator.py
backend/app/schemas/evidence.py
backend/app/schemas/verification.py
backend/app/api/v1/endpoints/verification.py
```

### 7.3. Пример результата верификации

```json
{
  "claim_id": "claim_001",
  "claim": "Скидка на товар достигает 70%",
  "verdict": "partially_supported",
  "confidence": 0.74,
  "evidence_summary": {
    "supporting": 3,
    "refuting": 1,
    "neutral": 2,
    "conflicting": true
  },
  "sources": [
    {
      "url": "https://example.com/source",
      "title": "Example source",
      "source_type": "official",
      "credibility_score": 0.86,
      "relevance_score": 0.91,
      "freshness_score": 0.78,
      "evidence_relation": "supports",
      "evidence_span": "..."
    }
  ],
  "explanation": "Утверждение частично подтверждается официальной страницей, однако найдено противоречие с условиями акции."
}
```

---

## 8. Формальная модель доказательной верификации

### 8.1. Claim

```text
c = {text, normalized_text, type, domain, timestamp, source_modality, risk_level}
```

### 8.2. Evidence item

```text
e = {source, text_span, url, date, source_type, relevance, credibility, freshness, independence, relation}
```

### 8.3. Evidence base

```text
E(c) = {e1, e2, ..., en}
```

### 8.4. Relation

```text
r(e, c) ∈ {supports, refutes, partially_supports, partially_refutes, neutral, insufficient}
```

### 8.5. Source credibility

```text
credibility(s) = f(authority, primary_source, domain_reputation, transparency, expertise, independence, history, citation_quality)
```

### 8.6. Evidence weight

```text
w(e, c) = α * relevance + β * credibility + γ * freshness + δ * independence + ε * specificity
```

### 8.7. Verdict

```text
v(c) ∈ {
  supported,
  likely_supported,
  partially_supported,
  conflicting,
  not_enough_evidence,
  likely_refuted,
  refuted
}
```

---

## 9. Классы вердиктов

| Вердикт | Описание |
|---|---|
| supported | утверждение подтверждается надежной доказательной базой |
| likely_supported | большинство надежных свидетельств поддерживает claim |
| partially_supported | часть утверждения подтверждается, часть требует уточнения |
| conflicting | доказательная база противоречива |
| not_enough_evidence | недостаточно свидетельств |
| likely_refuted | большинство надежных свидетельств опровергает claim |
| refuted | утверждение явно опровергается надежными источниками |

---

## 10. Источники данных

### 10.1. Входные данные из VeritasAd 2.0

- извлеченные claims;
- нормализованные claims;
- типы claims;
- risk level;
- source modality;
- timestamps;
- video/post metadata;
- brand signals.

### 10.2. Внешние источники

- официальные сайты брендов;
- маркетплейсы;
- страницы условий акций;
- пресс-релизы;
- новостные сайты;
- государственные реестры;
- документы и PDF;
- научные источники для health/science claims;
- финансовые и юридические источники для соответствующих claims;
- независимые обзоры;
- архивные версии страниц при необходимости.

### 10.3. Рекомендуемый размер датасета

- 1000–3000 claims;
- 5000–15000 evidence candidates;
- 3–7 evidence items на claim;
- 2–3 разметчика;
- разметка relations: support/refute/neutral/conflict;
- разметка source credibility;
- разметка итоговых вердиктов.

---

## 11. Схема датасета доказательной верификации

```text
data/
  datasets/
    verification/
      claims/
        claims_train.jsonl
        claims_val.jsonl
        claims_test.jsonl
      evidence/
        evidence_candidates.jsonl
        evidence_ranked.jsonl
      annotations/
        evidence_relations.jsonl
        source_credibility.jsonl
        verdicts.jsonl
      experiments/
        baseline_results.json
        ablation_results.json
      README.md
```

### 11.1. Формат claim

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

### 11.2. Формат evidence

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

### 11.3. Формат вердикта

```json
{
  "claim_id": "claim_001",
  "gold_verdict": "partially_supported",
  "confidence": 0.82,
  "rationale": "Официальный источник подтверждает наличие скидки до 70%, но только для части товаров."
}
```

---

## 12. Экспериментальный дизайн

### 12.1. Baseline-системы

| Система | Описание |
|---|---|
| LLM-only | модель отвечает без внешнего поиска |
| Search + LLM | обычный поиск и генерация ответа |
| Standard RAG | retrieval по семантической близости |
| RAG + reranker | RAG с reranking |
| RAG + source type | учет только типа источника |
| RAG + credibility | учет достоверности источника |
| RAG + contradiction | учет противоречий |
| Full VeritasAd 3.0 | полный метод |

### 12.2. Метрики evidence retrieval

- evidence precision@k;
- evidence recall@k;
- MRR;
- nDCG;
- hit@k.

### 12.3. Метрики evidence relation classification

- accuracy;
- macro-F1;
- confusion matrix;
- support/refute F1.

### 12.4. Метрики source credibility scoring

- Spearman correlation с экспертной оценкой;
- MAE/RMSE для числовой оценки;
- pairwise ranking accuracy.

### 12.5. Метрики verdict prediction

- accuracy;
- macro-F1;
- weighted-F1;
- balanced accuracy;
- Brier score;
- expected calibration error.

### 12.6. Метрики contradiction handling

- contradiction detection F1;
- conflict resolution accuracy;
- robustness under conflicting evidence;
- performance degradation under adversarial/noisy evidence.

### 12.7. Метрики explainability

- faithfulness;
- evidence coverage;
- human evaluation;
- citation correctness;
- hallucination rate.

---

## 13. Ablation study

Проверить вклад модулей:

```text
Full model
- без credibility scoring
- без freshness scoring
- без independence scoring
- без contradiction analysis
- без evidence relation classifier
- без reranking
- без claim normalization
- без calibrated confidence
```

---

## 14. Stress tests

Проверить систему на случаях:

- противоречивые источники;
- устаревшие источники;
- рекламные заинтересованные источники;
- шумные документы;
- нерелевантные top-k документы;
- claims с числовыми ограничениями;
- claims с временным контекстом;
- claims с частичной истинностью;
- claims с отсутствующей доказательной базой.

---

## 15. План аспирантуры по годам

## Год 1 — постановка научной проблемы и evidence retrieval

### Цель

Перейти от claim extraction к evidence retrieval и сформировать экспериментальную базу.

### Задачи

- [ ] Уточнить тему аспирантуры.
- [ ] Сформулировать объект, предмет, цель, задачи, гипотезу.
- [ ] Провести систематический обзор литературы по automated fact-checking, RAG, source credibility, contradiction detection.
- [ ] Расширить датасет claims из магистратуры.
- [ ] Реализовать query generation.
- [ ] Реализовать evidence retrieval.
- [ ] Реализовать baseline: search + LLM.
- [ ] Реализовать standard RAG baseline.
- [ ] Начать разметку evidence candidates.
- [ ] Подготовить первую статью по evidence retrieval.
- [ ] Описать формальную модель evidence item.

### Результаты года

- утвержденная тема;
- обзор литературы;
- расширенный claims dataset;
- evidence retrieval MVP;
- baseline-системы;
- первая статья;
- черновик главы 1.

---

## Год 2 — credibility-aware verification

### Цель

Разработать модель оценки достоверности источников и взвешенного ранжирования свидетельств.

### Задачи

- [ ] Формализовать признаки source credibility.
- [ ] Реализовать `source_credibility.py`.
- [ ] Реализовать `evidence_ranker.py`.
- [ ] Разработать функцию evidence weight.
- [ ] Разметить source credibility.
- [ ] Провести эксперименты по ранжированию evidence.
- [ ] Сравнить semantic-only retrieval и credibility-aware retrieval.
- [ ] Подготовить статью по source credibility / evidence ranking.
- [ ] Описать модель доказательной базы.
- [ ] Начать разработку evidence relation classifier.

### Результаты года

- модель credibility scoring;
- метод взвешенного evidence ranking;
- разметка источников;
- эксперименты;
- статья;
- черновик главы 2.

---

## Год 3 — contradiction analysis и verdict generation

### Цель

Добавить анализ противоречий и формирование итогового калиброванного вердикта.

### Задачи

- [ ] Реализовать `evidence_relation_classifier.py`.
- [ ] Реализовать `contradiction_analyzer.py`.
- [ ] Реализовать `evidence_aggregator.py`.
- [ ] Реализовать `verdict_generator.py`.
- [ ] Формализовать классы вердиктов.
- [ ] Разметить итоговые verdict labels.
- [ ] Провести ablation study.
- [ ] Провести stress tests на противоречивых источниках.
- [ ] Сравнить Full VeritasAd 3.0 с baseline.
- [ ] Подготовить статью по contradiction-aware verification.
- [ ] Описать главы 3–4.

### Результаты года

- полный метод VeritasAd 3.0;
- алгоритм анализа противоречий;
- калиброванный вердикт;
- основные экспериментальные результаты;
- статья;
- черновик глав 3–4.

---

## Год 4 — завершение диссертации и защита

Если аспирантура трехлетняя, часть задач четвертого года нужно перенести в конец третьего года.

### Цель

Оформить диссертацию, публикации и защитный пакет.

### Задачи

- [ ] Провести финальные эксперименты.
- [ ] Подготовить итоговые таблицы и графики.
- [ ] Завершить анализ ошибок.
- [ ] Описать ограничения метода.
- [ ] Подготовить reproducibility package.
- [ ] Опубликовать или подать финальную статью.
- [ ] Оформить диссертацию.
- [ ] Сформулировать положения на защиту.
- [ ] Подготовить автореферат.
- [ ] Подготовить презентацию.
- [ ] Подготовить demo VeritasAd 3.0.
- [ ] Защитить диссертацию.

### Результаты года

- завершенная кандидатская диссертация;
- публикации;
- воспроизводимые эксперименты;
- VeritasAd 3.0 release;
- подготовленная дальнейшая докторская линия.

---

## 16. План публикаций

### Публикация 1 — Evidence Retrieval

**Тема:** «Метод поиска внешних свидетельств для верификации рекламных утверждений»

Содержание:

- query generation;
- evidence retrieval;
- baseline RAG;
- метрики retrieval;
- первый датасет.

### Публикация 2 — Source Credibility

**Тема:** «Взвешенное ранжирование внешних свидетельств с учетом достоверности источников»

Содержание:

- признаки credibility;
- source scoring;
- evidence ranking;
- comparison with semantic-only ranking.

### Публикация 3 — Contradiction-Aware Verification

**Тема:** «Метод верификации утверждений в условиях противоречивой доказательной базы»

Содержание:

- evidence relation classification;
- contradiction analysis;
- evidence aggregation;
- verdict generation.

### Публикация 4 — Full System / VeritasAd 3.0

**Тема:** «Архитектура интеллектуальной системы доказательной верификации рекламного и медиаконтента»

Содержание:

- full pipeline;
- dataset;
- experiments;
- ablation study;
- practical validation.

---

## 17. GitHub roadmap VeritasAd 3.0

### Milestone 1 — Verification Foundation

- [ ] `docs/phd_research_roadmap.md`.
- [ ] `docs/verification_problem_statement.md`.
- [ ] `docs/evidence_schema.md`.
- [ ] `docs/source_credibility_model.md`.
- [ ] `docs/verification_metrics.md`.

### Milestone 2 — Evidence Retrieval

- [ ] `query_generator.py`.
- [ ] `evidence_retriever.py`.
- [ ] search API integration.
- [ ] evidence candidate storage.
- [ ] evidence retrieval evaluation.
- [ ] retrieval baseline scripts.

### Milestone 3 — Source Credibility

- [ ] `source_credibility.py`.
- [ ] source type classifier.
- [ ] freshness scorer.
- [ ] independence estimator.
- [ ] credibility annotation schema.
- [ ] credibility experiments.

### Milestone 4 — Evidence Relations

- [ ] `evidence_relation_classifier.py`.
- [ ] support/refute/neutral classifier.
- [ ] partial support/refute handling.
- [ ] NLI baseline.
- [ ] relation annotation tools.

### Milestone 5 — Contradiction Analysis

- [ ] `contradiction_analyzer.py`.
- [ ] conflict graph.
- [ ] contradiction metrics.
- [ ] stress-test dataset.
- [ ] contradiction experiment report.

### Milestone 6 — Verdict Generation

- [ ] `evidence_aggregator.py`.
- [ ] `verdict_generator.py`.
- [ ] calibrated confidence.
- [ ] explainable report generator.
- [ ] frontend verification report.

### Milestone 7 — Thesis Package

- [ ] final datasets.
- [ ] experiment scripts.
- [ ] reproducibility package.
- [ ] dissertation text.
- [ ] defense presentation.
- [ ] release `v3.0-phd`.

---

## 18. Рекомендуемая структура кандидатской диссертации

## Глава 1. Анализ проблемы доказательной верификации цифрового контента

### 1.1. Цифровой медиаконтент как источник проверяемых утверждений

Описать рекламный и медиаконтент, типы claims, риски недостоверных утверждений.

### 1.2. Методы automated fact-checking

Разобрать claim extraction, evidence retrieval, veracity prediction, explanation generation.

### 1.3. LLM и RAG в задачах верификации

Показать возможности и ограничения LLM/RAG.

### 1.4. Оценка достоверности источников

Рассмотреть source credibility, trustworthiness, authority, primary/secondary sources.

### 1.5. Проблема противоречивой доказательной базы

Показать, почему standard RAG недостаточен.

### 1.6. Постановка научной задачи

Объект, предмет, цель, задачи, гипотеза, научная новизна.

---

## Глава 2. Модели доказательной базы и достоверности источников

### 2.1. Формальная модель проверяемого утверждения

Claim, claim type, domain, risk, context.

### 2.2. Модель внешнего свидетельства

Evidence item, source, date, span, relation.

### 2.3. Модель достоверности источника

Credibility features, scoring function.

### 2.4. Модель доказательной базы

Evidence set, evidence graph, conflict graph.

### 2.5. Модель противоречий

Типы противоречий: прямые, частичные, временные, контекстные.

### 2.6. Модель итогового вердикта

Классы вердиктов и confidence.

---

## Глава 3. Методы доказательной верификации утверждений

### 3.1. Генерация поисковых запросов

Query generation на основе normalized claim.

### 3.2. Поиск внешних свидетельств

Hybrid retrieval, dense retrieval, search APIs, reranking.

### 3.3. Взвешенное ранжирование свидетельств

Relevance + credibility + freshness + independence.

### 3.4. Классификация отношения evidence к claim

Supports, refutes, neutral, partial.

### 3.5. Анализ противоречий

Conflict detection and resolution.

### 3.6. Агрегация доказательной базы

Evidence aggregation and calibrated verdict.

### 3.7. Архитектура VeritasAd 3.0

Описание модулей, API, pipeline, storage.

---

## Глава 4. Экспериментальная оценка

### 4.1. Датасет

Claims, evidence, sources, labels.

### 4.2. Разметка

Annotation guidelines, annotators, agreement.

### 4.3. Baseline-системы

LLM-only, standard RAG, RAG+reranker и другие.

### 4.4. Метрики

Retrieval, relation classification, verdict prediction, calibration, explainability.

### 4.5. Основные эксперименты

Сравнение методов.

### 4.6. Ablation study

Вклад каждого модуля.

### 4.7. Stress tests

Противоречивые, устаревшие и недостоверные источники.

### 4.8. Анализ ошибок

Классы ошибок и ограничения.

---

## Глава 5. Практическая апробация и программная реализация

### 5.1. Реализация VeritasAd 3.0

Backend, frontend, data pipeline.

### 5.2. Сценарии применения

Реклама, медиа, маркетплейсы, мониторинг claims.

### 5.3. Оценка производительности

Время обработки, масштабируемость, отказоустойчивость.

### 5.4. Ограничения и этические вопросы

Неполные данные, bias, приватность, юридические риски.

### 5.5. Перспективы развития

Докторская линия и расширение на общий цифровой контент.

---

## 19. Минимальный результат для успешной аспирантуры

К защите должно быть:

- [ ] формальная модель доказательной базы;
- [ ] метод evidence retrieval;
- [ ] метод source credibility scoring;
- [ ] метод contradiction analysis;
- [ ] метод evidence aggregation;
- [ ] калиброванный verdict generator;
- [ ] размеченный датасет claims + evidence;
- [ ] baseline comparison;
- [ ] ablation study;
- [ ] stress tests;
- [ ] 3–4 публикации;
- [ ] воспроизводимый экспериментальный пакет;
- [ ] программная реализация VeritasAd 3.0;
- [ ] положения на защиту.

---

## 20. Риски аспирантуры и способы их снизить

| Риск | Что может пойти не так | Как снизить |
|---|---|---|
| Тема слишком широкая | работа расползется на весь fact-checking | ограничить домен рекламным/медийным контентом |
| RAG выглядит не новым | совет скажет, что это уже известно | сделать вклад в credibility + contradiction + evidence aggregation |
| Source credibility спорна | трудно объективно оценить источник | формализовать признаки и экспертную разметку |
| Недостаточно данных | слабая экспериментальная база | начать сбор данных еще в магистратуре |
| LLM не воспроизводимы | закрытые модели меняются | использовать open-source baseline и сохранять outputs |
| Верификация превращается в продукт | мало науки, много интерфейса | держать фокус на моделях, алгоритмах, метриках |
| Противоречия сложно размечать | низкое agreement | подготовить строгую annotation guideline |
| Слабые публикации | трудно выйти на защиту | планировать статьи по модулям |
| Юридические риски | система может ошибочно обвинять рекламу | формулировать вердикты как доказательную оценку, а не юридическое заключение |

---

## 21. Докторская перспектива после аспирантуры

После кандидатской можно развивать тему в докторскую линию:

> **Методология интеллектуальной доказательной верификации цифрового контента в условиях неполной, противоречивой и разнонадежной информационной среды.**

Докторская линия может включать:

- обобщение с рекламы на новости, социальные сети, образовательный и научно-популярный контент;
- мультиязычную верификацию;
- мультимодальные claims: текст + изображение + видео + аудио;
- temporal verification;
- knowledge graph evidence;
- human-in-the-loop verification;
- trust-aware AI systems;
- регуляторные и этические аспекты.

---

## 22. Итоговая цель аспирантуры

К окончанию аспирантуры VeritasAd должен стать системой:

```text
VeritasAd 3.0 =
Claim extraction
+ query generation
+ evidence retrieval
+ source credibility scoring
+ evidence relation classification
+ contradiction analysis
+ evidence aggregation
+ calibrated verdict
+ explainable report
+ reproducible experiments
```

Главный научный результат:

> **Разработан и экспериментально подтвержден метод доказательной верификации проверяемых утверждений в цифровом медиаконтенте, устойчивый к неполной, противоречивой и разнонадежной внешней доказательной базе.**

Главный практический результат:

> **Создана исследовательская платформа VeritasAd 3.0, позволяющая извлекать claims из рекламного и медиаконтента, находить внешние свидетельства, оценивать их достоверность, выявлять противоречия и формировать объяснимый калиброванный вердикт.**
