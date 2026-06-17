# Датасеты: схемы и руководства по разметке

Этот раздел содержит **документацию** датасетов VeritasAd: схемы данных и руководства по разметке. **Самих данных здесь нет** — здесь живут только спецификации форматов и инструкции для аннотаторов.

> **ВАЖНО.** Сами данные хранятся в `../../../data/datasets/` (подкаталоги `claims/` и `verification/`). Крупные и сырые файлы там git-ignored и в репозиторий не попадают — версионируется только их документация в этом разделе.

## Структура раздела

Раздел разбит по трекам исследования:

### `claims/` — master-трек (VeritasAd 2.0)

Датасеты для извлечения утверждений (claims) из рекламных материалов.

- [Схема данных](./claims/schema.md) — `./claims/schema.md`
- [Руководство по разметке](./claims/annotation-guidelines.md) — `./claims/annotation-guidelines.md`

### `verification/` — phd-трек (VeritasAd 3.0)

Датасеты для верификации утверждений (fact-checking / проверка достоверности).

- [Схема данных](./verification/schema.md) — `./verification/schema.md`
- [Руководство по разметке](./verification/annotation-guidelines.md) — `./verification/annotation-guidelines.md`

## Где лежат сами данные

Документация (в этом разделе) и данные (в `data/`) разделены намеренно:

```text
docs/research/datasets/        <- ВЫ ЗДЕСЬ: схемы и руководства (версионируются)
  claims/
  verification/

../../../data/datasets/        <- сами данные (крупные/сырые файлы git-ignored)
  claims/
  verification/
```

При добавлении нового датасета сначала опишите его схему и правила разметки здесь, затем кладите данные в соответствующий подкаталог `../../../data/datasets/`.

## Шаблон карточки датасета

Каждый датасет описывается карточкой по единому шаблону: [dataset-card.template.md](../_templates/dataset-card.template.md) — `../_templates/dataset-card.template.md`.

## Навигация

- [Назад к хабу исследовательского воркспейса](../README.md) — `../README.md`
