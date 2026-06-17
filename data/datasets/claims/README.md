# Датасет claims (трек master)

Эта директория хранит **фактические данные** датасета claims (сырые медиа, обработанные артефакты, разметку и сплиты), а **не документацию**. Описание схемы и правил разметки см. в разделе «Схема и разметка» ниже.

## Структура

```text
raw/
  videos/
  posts/
  screenshots/
processed/
  transcripts/
  ocr/
  metadata/
annotations/
splits/
```

- `raw/` — исходные материалы как они были собраны: видео, посты, скриншоты.
- `processed/` — производные артефакты: транскрипты, результаты OCR, метаданные.
- `annotations/` — файлы разметки (claims) в формате JSONL.
- `splits/` — определения разбиений (train/val/test) в формате JSONL.

## Что коммитится

- `.gitkeep` — чтобы пустые директории попадали в репозиторий.
- Этот `README`.
- Мелкие `*.jsonl` — содержимое `annotations/` и `splits/`.

Сырые медиа и крупные бинарные файлы **не коммитятся** (git-ignored) — см. правила в [../.gitignore](../.gitignore).

## Схема и разметка

- Схема JSONL: [../../../docs/research/datasets/claims/schema.md](../../../docs/research/datasets/claims/schema.md)
- Правила разметки: [../../../docs/research/datasets/claims/annotation-guidelines.md](../../../docs/research/datasets/claims/annotation-guidelines.md)
