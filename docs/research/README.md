# VeritasAd Research Workspace

Единое расширяемое пространство для исследовательских артефактов VeritasAd. Проект развивается по
двум трекам, у каждого — свой roadmap-источник истины:

- **VeritasAd 2.0 — магистратура** (извлечение и классификация проверяемых рекламных утверждений,
  milestone'ы M1–M5, 4 семестра). Источник: [`roadmaps/master-2.0.md`](roadmaps/master-2.0.md).
- **VeritasAd 3.0 — аспирантура** (доказательная верификация утверждений, milestone'ы M1–M7, 4 года).
  Источник: [`roadmaps/phd-3.0.md`](roadmaps/phd-3.0.md).

Workspace организован **по типу артефакта**; внутри каждого типа артефакты разделены на фазы
`master/` (2.0) и `phd/` (3.0). Переиспользуемые между фазами материалы лежат в `shared/`.

> Это исследовательская зона. Продакшн-код, бизнес-логика и инженерные правила репозитория
> описаны в [`../../AGENTS.md`](../../AGENTS.md) и сопутствующих governance-доках в `docs/`.

---

## Навигация

| Раздел | Что внутри |
|---|---|
| [`roadmaps/`](roadmaps/README.md) | Roadmap'ы обоих треков (источники истины по milestone'ам). |
| [`prompts/`](prompts/README.md) | Переиспользуемые системные промпты (`shared/`) и исследовательские промпты (`master/`, `phd/`). |
| [`plans/`](plans/README.md) | Планы реализации milestone'ов (Context → scope → шаги → verification). |
| [`specs/`](specs/README.md) | Дизайн-спеки модулей и методов. |
| [`reports/`](reports/README.md) | Отчёты: эксперименты, ablation, error analysis, annotation agreement. |
| [`experiments/`](experiments/README.md) | Реестр и конфиги экспериментов (baseline, ablation). |
| [`datasets/`](datasets/README.md) | **Документация** датасетов: схемы JSONL и annotation guidelines (не сами данные). |
| [`literature/`](literature/README.md) | Обзор литературы, заметки по источникам, проверка новизны. |
| [`_templates/`](_templates/) | Шаблоны для всех типов артефактов. |

Сами данные (сырые/процессированные/разметка/сплиты) живут вне этого дерева — в
[`../../data/datasets/`](../../data/datasets/) (крупные/сырые файлы не коммитятся, см. его `.gitignore`).

---

## Структура

```
docs/research/
├── README.md                # этот файл
├── _templates/              # 8 шаблонов артефактов
├── roadmaps/                # master-2.0.md · phd-3.0.md
├── prompts/                 # shared/ · master/ · phd/
├── plans/                   # master/ · phd/
├── specs/                   # master/ · phd/
├── reports/                 # master/ · phd/
├── experiments/             # master/ · phd/
├── datasets/                # claims/ (master) · verification/ (phd)  — схемы и guidelines
└── literature/              # related-work.md и заметки по источникам
```

---

## Конвенции

### Именование

- **Датируемые артефакты** (plans / specs / reports / experiments): `YYYY-MM-DD-<milestone>-<slug>.md`,
  напр. `2026-09-01-m2-claim-extractor-mvp.md`. Фаза кодируется **папкой** (`plans/master/`),
  milestone — **префиксом имени** (`m2`).
- **Промпты:** `<slug>.md` в `prompts/{shared,master,phd}/`; версия — суффиксом `-vN`
  (напр. `ultimate-prompt-v3.md`).
- **Заметки по литературе:** `<bib-key>.md` или `<slug>.md` в `literature/`.
- Имена существующих перенесённых файлов **не меняем** ради устойчивости ссылок.

### Frontmatter

Каждый артефакт (plans / specs / reports / experiments / prompts / literature-note) открывается
YAML-frontmatter:

```yaml
---
id:                      # стабильный kebab-идентификатор, напр. m2-claim-extractor-mvp
title:                   # человекочитаемый заголовок
phase: master            # master (2.0) | phd (3.0) | shared
milestone: M2            # M1..M5 (master) | M1..M7 (phd); опустить для prompts/literature
status: draft            # planned | draft | in-review | approved | done
date: 2026-06-16         # YYYY-MM-DD
author:                  # имя/ник
related: []              # относительные пути к связанным артефактам
---
```

Сразу под frontmatter — человекочитаемый статус-блок, как в существующей M2-спеке:

```markdown
> **Статус: ЧЕРНОВИК.** Краткий контекст текущего состояния документа.
```

### Жизненный цикл статуса

```
planned → draft → in-review → approved → done
```

| Статус | Человекочитаемо | Значение |
|---|---|---|
| `planned` | ЗАПЛАНИРОВАН | артефакт намечен, содержимого ещё нет |
| `draft` | ЧЕРНОВИК | в активной разработке |
| `in-review` | НА РЕВЬЮ | готов, проходит self-review / пользовательское ревью |
| `approved` | СОГЛАСОВАН | принят, можно опираться |
| `done` | ЗАВЕРШЁН | исполнен/опубликован, дальше не меняется |

### Фаза

- `master` — относится к VeritasAd 2.0 (магистратура);
- `phd` — относится к VeritasAd 3.0 (аспирантура);
- `shared` — переиспользуется между треками (например, системные промпты).

---

## Milestone-карта

Milestone'ы — источник истины в roadmap'ах. Разделы workspace наполняются артефактами под
соответствующие milestone'ы.

### Master 2.0 — см. [`roadmaps/master-2.0.md` §14](roadmaps/master-2.0.md)

| Milestone | Тема | Куда кладём артефакты |
|---|---|---|
| M1 | Research Foundation | `plans/master/`, `literature/`, `datasets/claims/` |
| M2 | Claim Extraction MVP | `plans/master/`, `specs/master/` |
| M3 | Dataset Pipeline | `datasets/claims/`, `plans/master/` |
| M4 | Experiments | `experiments/master/`, `reports/master/` |
| M5 | Thesis Package | `reports/master/` |

### PhD 3.0 — см. [`roadmaps/phd-3.0.md` §17](roadmaps/phd-3.0.md)

| Milestone | Тема | Куда кладём артефакты |
|---|---|---|
| M1 | Verification Foundation | `specs/phd/`, `literature/`, `datasets/verification/` |
| M2 | Evidence Retrieval | `specs/phd/`, `experiments/phd/` |
| M3 | Source Credibility | `specs/phd/`, `datasets/verification/` |
| M4 | Evidence Relations | `specs/phd/`, `datasets/verification/` |
| M5 | Contradiction Analysis | `experiments/phd/`, `reports/phd/` |
| M6 | Verdict Generation | `specs/phd/`, `reports/phd/` |
| M7 | Thesis Package | `reports/phd/` |

---

## Соответствие путей (плоские имена из roadmap → новая структура)

Roadmap'ы ссылаются на «плоские» документы (`docs/*.md`). Их новые адреса в этой структуре:

| Путь из roadmap | Новый путь |
|---|---|
| `docs/research_roadmap.md` / `docs/master_thesis_plan.md` | [`roadmaps/master-2.0.md`](roadmaps/master-2.0.md) (+ [`plans/master/`](plans/README.md)) |
| `docs/dataset_schema.md` | [`datasets/claims/schema.md`](datasets/claims/schema.md) |
| `docs/annotation_guidelines.md` | [`datasets/claims/annotation-guidelines.md`](datasets/claims/annotation-guidelines.md) |
| `docs/experiments.md` | [`experiments/master/`](experiments/README.md) |
| `docs/phd_research_roadmap.md` | [`roadmaps/phd-3.0.md`](roadmaps/phd-3.0.md) |
| `docs/verification_problem_statement.md` | [`specs/phd/`](specs/README.md) |
| `docs/evidence_schema.md` | [`datasets/verification/schema.md`](datasets/verification/schema.md) |
| `docs/source_credibility_model.md` / `docs/verification_metrics.md` | [`specs/phd/`](specs/README.md) |

---

## Как добавить артефакт

1. Определи **тип** (plan / spec / report / experiment / prompt / dataset-doc / literature-note)
   и **фазу** (`master` / `phd` / `shared`).
2. Скопируй соответствующий шаблон из [`_templates/`](_templates/).
3. Назови файл по конвенции (`YYYY-MM-DD-<milestone>-<slug>.md` для датируемых).
4. Заполни frontmatter и статус-блок; проставь `related` на связанные артефакты.
5. Если артефакт закрывает пункт milestone — отметь его в соответствующем roadmap.

---

## Связанные правила

- [`../../AGENTS.md`](../../AGENTS.md) — операционный контракт репозитория (move-before-rewrite,
  preserve behavior, формат коммитов, ветки `docs/*`).
- [`../execution-checklists.md`](../execution-checklists.md) — чек-листы выполнения (зеркалятся в шаблоне плана).
- [`../decision-log.md`](../decision-log.md) — журнал архитектурных решений.
- [`../../GEMINI.md`](../../GEMINI.md) — контекст-файл Gemini CLI (остаётся в корне репозитория).
