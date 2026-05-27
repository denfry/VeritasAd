# Dataset Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich ML dataset pipeline with language metadata, add language-specific collection profiles (en, zh, es, ar, hi), increase dataset size from 88 to ~300-500 records, and add stratified splitting by label + language.

**Architecture:** Extend `BatchProfile` with `language` field → add multi-language profiles → extend `NormalizedAdRecord` with language → stratified split → CLI review helper → run collection.

**Tech Stack:** Python 3.12, JSONL, scikit-learn (for stratification)

---

### Task 1: Add language field to BatchProfile

**Files:**
- Modify: `backend/app/ml/ad_batch.py`

- [ ] **Step 1: Add language field to BatchProfile dataclass**

Find `BatchProfile` in `ad_batch.py` and add `language: str` field after `name`:

```python
@dataclass(frozen=True)
class BatchProfile:
    name: str
    language: str  # ISO 639-1 language code
    expected_label: str
    video_queries: tuple[str, ...]
    telegram_channels: tuple[str, ...] = ()
    reviewer_hint: str = ""
```

- [ ] **Step 2: Add language to build_manifest (no change needed — manifest uses profile fields generically)**

- [ ] **Step 3: Combine profile records — add language to output rows**

In `combine_profile_records`, add:
```python
row["language"] = profile.language
```

- [ ] **Step 4: Run existing tests to check nothing broke**

Run: `cd backend && uv run pytest tests/ -x -q`
Expected: All tests pass

---

### Task 2: Add multi-language profiles

**Files:**
- Modify: `backend/app/ml/ad_batch.py`

- [ ] **Step 1: Update DEFAULT_BATCH_PROFILES with language variants**

Replace the existing `DEFAULT_BATCH_PROFILES` with an extended version that includes per-language profiles:

```python
DEFAULT_BATCH_PROFILES: dict[str, BatchProfile] = {
    # --- Russian ---
    "official_ru": BatchProfile(
        name="official_ru", language="ru", expected_label="official",
        video_queries=(
            "#ad спонсор промокод обзор",
            "платное партнерство реклама скидка",
            "спонсировано реклама промокод обзор",
        ),
        telegram_channels=("banksta", "vcnews", "rozetked"),
        reviewer_hint="Paid promotion with explicit disclosure (#ad, #реклама, ERID, or paid partnership).",
    ),
    "hidden_ad_ru": BatchProfile(
        name="hidden_ad_ru", language="ru", expected_label="hidden_ad",
        video_queries=(
            "партнерская ссылка промокод скидка обзор",
            "купон промокод ссылка в описании обзор",
            "промокод эксклюзивная скидка без раскрытия",
        ),
        telegram_channels=("thevillage",),
        reviewer_hint="Commercial CTA, affiliate/coupon link, or sales script without clear disclosure.",
    ),
    "mention_ru": BatchProfile(
        name="mention_ru", language="ru", expected_label="mention",
        video_queries=(
            "обзор техники распаковка сравнение",
            "обзор товара без партнерской ссылки",
            "новости бренда анализ обзор",
        ),
        telegram_channels=("banksta", "meduzalive"),
        reviewer_hint="Brand appears or is discussed, but the content is not primarily promotional.",
    ),
    "no_ad_ru": BatchProfile(
        name="no_ad_ru", language="ru", expected_label="no_ad",
        video_queries=(
            "туториал как сделать проект",
            "новости анализ сегодня",
            "образовательная лекция объяснение",
        ),
        telegram_channels=("meduzalive", "tproger", "durov"),
        reviewer_hint="No meaningful brand promotion, CTA, disclosure, or commercial link evidence.",
    ),

    # --- English ---
    "official_en": BatchProfile(
        name="official_en", language="en", expected_label="official",
        video_queries=(
            "#ad sponsored review promo code",
            "paid partnership #sponsored discount code",
            "sponsored by use code discount review",
        ),
        reviewer_hint="Paid promotion with an explicit disclosure marker such as #ad, #sponsored, ERID, or paid partnership.",
    ),
    "hidden_ad_en": BatchProfile(
        name="hidden_ad_en", language="en", expected_label="hidden_ad",
        video_queries=(
            "affiliate link discount code review",
            "coupon code link in description review",
            "promo code exclusive discount no sponsored disclosure",
        ),
        reviewer_hint="Commercial CTA, affiliate/coupon link, or sales script without clear disclosure.",
    ),
    "mention_en": BatchProfile(
        name="mention_en", language="en", expected_label="mention",
        video_queries=(
            "tech review unboxing comparison",
            "product review no affiliate link",
            "brand news analysis review",
        ),
        reviewer_hint="Brand appears or is discussed, but the content is not primarily promotional.",
    ),
    "no_ad_en": BatchProfile(
        name="no_ad_en", language="en", expected_label="no_ad",
        video_queries=(
            "tutorial how to build project",
            "news analysis today no sponsor",
            "educational explanation lecture",
        ),
        telegram_channels=("durov", "tproger"),
        reviewer_hint="No meaningful brand promotion, CTA, disclosure, or commercial link evidence.",
    ),

    # --- Chinese ---
    "official_zh": BatchProfile(
        name="official_zh", language="zh", expected_label="official",
        video_queries=(
            "赞助 推广 优惠码 评测",
            "付费合作 广告 折扣码 review",
        ),
        reviewer_hint="Paid promotion with explicit disclosure marker in Chinese.",
    ),
    "hidden_ad_zh": BatchProfile(
        name="hidden_ad_zh", language="zh", expected_label="hidden_ad",
        video_queries=(
            "联盟营销 折扣码 评测 开箱",
            "优惠券 推广链接 评测 推荐",
        ),
        reviewer_hint="Affiliate link or coupon code with commercial intent.",
    ),
    "mention_zh": BatchProfile(
        name="mention_zh", language="zh", expected_label="mention",
        video_queries=(
            "开箱 评测 对比 2025",
            "产品体验 使用感受 分享",
        ),
        reviewer_hint="Brand mention in a review or unboxing without clear ad intent.",
    ),
    "no_ad_zh": BatchProfile(
        name="no_ad_zh", language="zh", expected_label="no_ad",
        video_queries=(
            "教程 教学 编程 入门",
            "新闻 分析 报告 财经",
        ),
        reviewer_hint="No meaningful brand promotion, CTA, disclosure, or commercial link evidence.",
    ),

    # --- Spanish ---
    "official_es": BatchProfile(
        name="official_es", language="es", expected_label="official",
        video_queries=(
            "código de descuento reseña patrocinada",
            "publicidad pagada cupón descuento review",
        ),
        reviewer_hint="Paid promotion with explicit disclosure in Spanish.",
    ),
    "mention_es": BatchProfile(
        name="mention_es", language="es", expected_label="mention",
        video_queries=(
            "reseña análisis producto 2025",
            "review sin enlace de afiliado",
        ),
        reviewer_hint="Brand mention without clear promotional intent.",
    ),
    "no_ad_es": BatchProfile(
        name="no_ad_es", language="es", expected_label="no_ad",
        video_queries=(
            "tutorial cómo hacer proyecto",
            "noticias análisis explicación",
        ),
        reviewer_hint="No meaningful brand promotion evidence.",
    ),

    # --- Arabic ---
    "official_ar": BatchProfile(
        name="official_ar", language="ar", expected_label="official",
        video_queries=(
            "رمز ترويجي مراجعة رعاية",
            "إعلان مدفوع رمز خصم review",
        ),
        reviewer_hint="Paid promotion with explicit disclosure in Arabic.",
    ),
    "mention_ar": BatchProfile(
        name="mention_ar", language="ar", expected_label="mention",
        video_queries=(
            "مراجعة منتج مقارنة 2025",
            "تحليل أخبار تقييم",
        ),
        reviewer_hint="Brand mention without clear promotional intent.",
    ),
    "no_ad_ar": BatchProfile(
        name="no_ad_ar", language="ar", expected_label="no_ad",
        video_queries=(
            "شرح تعليمي برمجة للمبتدئين",
            "أخبار تحليل اقتصادي",
        ),
        reviewer_hint="No meaningful brand promotion evidence.",
    ),

    # --- Hindi ---
    "official_hi": BatchProfile(
        name="official_hi", language="hi", expected_label="official",
        video_queries=(
            "प्रायोजित समीक्षा प्रोमो कोड",
            "स्पॉन्सर्ड डिस्काउंट कोड समीक्षा",
        ),
        reviewer_hint="Paid promotion with explicit disclosure in Hindi.",
    ),
    "mention_hi": BatchProfile(
        name="mention_hi", language="hi", expected_label="mention",
        video_queries=(
            "समीक्षा अनबॉक्सिंग तुलना 2025",
            "उत्पाद समीक्षा बिना affiliate link",
        ),
        reviewer_hint="Brand mention without clear promotional intent.",
    ),
    "no_ad_hi": BatchProfile(
        name="no_ad_hi", language="hi", expected_label="no_ad",
        video_queries=(
            "ट्यूटोरियल प्रोजेक्ट कैसे बनाएं",
            "समाचार विश्लेषण शिक्षा",
        ),
        reviewer_hint="No meaningful brand promotion evidence.",
    ),
}
```

- [ ] **Step 2: Run existing tests**

Run: `cd backend && uv run pytest tests/ -x -q`
Expected: All tests pass

---

### Task 3: Add language field to NormalizedAdRecord

**Files:**
- Modify: `backend/app/ml/ad_dataset.py`

- [ ] **Step 1: Add language field to NormalizedAdRecord**

```python
@dataclass(frozen=True)
class NormalizedAdRecord:
    raw: dict[str, Any]
    record_id: str
    source_key: str
    label: str
    text: str
    features: dict[str, float]
    language: str  # ISO 639-1 — new field
    needs_review: bool
    has_text_encoding_warning: bool
```

- [ ] **Step 2: Update validate_record to extract language**

In `validate_record`, after `source_key = _source_key(record)`, add:
```python
language = str(record.get("language") or "ru").strip()
if language not in ("ru", "en", "zh", "es", "ar", "hi"):
    language = "ru"
```

Update the `NormalizedAdRecord(...)` return to include `language=language`.

- [ ] **Step 3: Update existing tests that construct NormalizedAdRecord**

Read tests:
```bash
cat backend/tests/unit/test_ml_dataset.py
```

Add `language="ru"` to any test `NormalizedAdRecord(...)` constructions.

- [ ] **Step 4: Run tests**

Run: `cd backend && uv run pytest tests/ -x -q`
Expected: All tests pass

---

### Task 4: Add stratified split by label + language

**Files:**
- Modify: `backend/app/ml/ad_dataset.py`

- [ ] **Step 1: Update split_records to use stratification**

Add `from collections import Counter` at top.

Rewrite `split_records`:

```python
def split_records(
    records: list[NormalizedAdRecord],
    *,
    seed: int = 20260505,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> DatasetSplit:
    if val_ratio < 0 or test_ratio < 0 or val_ratio + test_ratio >= 1:
        raise DatasetValidationError("val_ratio and test_ratio must be non-negative and sum to < 1")

    by_source: dict[str, NormalizedAdRecord] = {}
    for record in records:
        if record.source_key in by_source:
            raise DatasetValidationError(f"duplicate source: {record.source_key}")
        by_source[record.source_key] = record

    shuffled = list(by_source.values())
    rng = random.Random(seed)
    rng.shuffle(shuffled)

    total = len(shuffled)
    test_count = max(1, int(round(total * test_ratio))) if total >= 3 and test_ratio > 0 else 0
    val_count = max(1, int(round(total * val_ratio))) if total >= 3 and val_ratio > 0 else 0

    if val_count + test_count >= total:
        overflow = val_count + test_count - total + 1
        val_count = max(0, val_count - overflow)

    # Stratified grouping: ensure each (label, language) group appears in all splits
    groups: dict[tuple[str, str], list[NormalizedAdRecord]] = {}
    for record in shuffled:
        key = (record.label, record.language)
        groups.setdefault(key, []).append(record)

    train: list[NormalizedAdRecord] = []
    val: list[NormalizedAdRecord] = []
    test: list[NormalizedAdRecord] = []

    for group_records in groups.values():
        group_rng = random.Random(seed)
        group_rng.shuffle(group_records)
        n = len(group_records)
        n_test = max(0, min(len(test), int(round(n * test_ratio / max(1, test_ratio + val_ratio + 1)))))
        n_val = max(0, min(len(val), int(round(n * val_ratio / max(1, test_ratio + val_ratio + 1)))))
        # Simple: allocate proportionally
        n_test = max(1, int(round(n * test_ratio))) if n >= 3 and test_ratio > 0 else 0
        n_val = max(1, int(round(n * val_ratio))) if n >= 3 and val_ratio > 0 else 0
        remaining = n - n_test - n_val
        if remaining <= 0 and n > 0:
            n_test = max(0, min(n_test, n - 1))
            n_val = max(0, min(n_val, n - n_test - 1))
            remaining = n - n_test - n_val
        test.extend(group_records[:n_test])
        val.extend(group_records[n_test:n_test + n_val])
        train.extend(group_records[n_test + n_val:])

    return DatasetSplit(train=train, val=val, test=test)
```

- [ ] **Step 2: Run tests**

Run: `cd backend && uv run pytest tests/ -x -q`
Expected: All tests pass

---

### Task 5: Create CLI batch review helper

**Files:**
- Create: `backend/scripts/batch_review.py`

- [ ] **Step 1: Create batch_review.py**

```python
from __future__ import annotations

import json
import sys
from pathlib import Path

LABEL_OPTIONS = ("no_ad", "mention", "official", "unofficial", "hidden_ad")
LABEL_SHORTCUTS = {str(i): label for i, label in enumerate(LABEL_OPTIONS, start=1)}


def load_review_queue(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def load_existing_labels(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    labels = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rid = str(row.get("record_id", "")).strip()
            label = str(row.get("review_label", "")).strip()
            if rid and label:
                labels[rid] = label
    return labels


def save_label(labels_path: Path, record_id: str, label: str) -> None:
    rows = []
    if labels_path.exists():
        for line in labels_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("record_id") != record_id:
                    rows.append(row)
    rows.append({"record_id": record_id, "review_label": label})
    labels_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="CLI ad dataset review helper.")
    parser.add_argument("review_queue", type=Path, help="Path to review_queue.jsonl")
    parser.add_argument("--labels-output", type=Path, default=None,
                        help="Path to review_labels.jsonl (default: same dir as review queue)")
    args = parser.parse_args()

    records = load_review_queue(args.review_queue)
    labels_path = args.labels_output or (args.review_queue.parent / "review_labels.jsonl")
    existing = load_existing_labels(labels_path)

    print(f"Loaded {len(records)} records for review, {len(existing)} already labeled.")
    print()
    print("Shortcuts:")
    for key, label in LABEL_SHORTCUTS.items():
        print(f"  {key} → {label}")
    print("  s → skip (keep needs_review)")
    print("  q → quit and save")
    print()

    for i, record in enumerate(records):
        rid = str(record.get("record_id", "")).strip()
        if rid in existing:
            print(f"[{i+1}/{len(records)}] SKIP (already labeled: {existing[rid]}) — {rid}")
            continue

        title = str(record.get("title", ""))[:80]
        desc = str(record.get("description_excerpt", ""))[:200]
        transcript = str(record.get("transcript_excerpt", ""))[:200]
        batch_profile = str(record.get("batch_profile", ""))
        expected_label = str(record.get("expected_review_label", ""))

        print(f"\n--- Record {i+1}/{len(records)} ---")
        print(f"ID:       {rid}")
        print(f"Profile:  {batch_profile} (expected: {expected_label})")
        if title:
            print(f"Title:    {title}")
        if desc:
            print(f"Desc:     {desc}")
        if transcript:
            print(f"Transcript: {transcript}")
        print()

        while True:
            choice = input("Label (1-5, s, q): ").strip().lower()
            if choice == "q":
                print(f"\nSaved progress. {len(existing)} labels written to {labels_path}")
                return 0
            if choice == "s":
                break
            if choice in LABEL_SHORTCUTS:
                label = LABEL_SHORTCUTS[choice]
                save_label(labels_path, rid, label)
                existing[rid] = label
                print(f"  → {label}")
                break
            print("Invalid choice. Try again.")

    print(f"\nReview complete. {len(existing)} total labels written to {labels_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run a quick syntax check**

Run: `cd backend && uv run python -c "import ast; ast.parse(open('scripts/batch_review.py').read()); print('OK')"`
Expected: OK

---

### Task 6: Run collection

**Files:**
- Output: `data/annotated/balanced_ad_training_batch/`

- [ ] **Step 1: Generate batch plan (dry run)**

```bash
cd backend
uv run python scripts/collect_ad_training_batch.py \
  --videos-per-profile=30 \
  --posts-per-profile=30
```

Expected: Prints manifest path and commands. Review the manifest to verify all profiles are included.

- [ ] **Step 2: Run collection**

```bash
cd backend
uv run python scripts/collect_ad_training_batch.py \
  --videos-per-profile=30 \
  --posts-per-profile=30 \
  --run
```

Expected: Progress output for each profile, final consolidation summary with record counts.

- [ ] **Step 3: Verify dataset integrity**

```bash
uv run python -c "
from pathlib import Path
import json
path = Path('../data/annotated/balanced_ad_training_batch/dataset.jsonl')
records = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
print(f'Total records: {len(records)}')
from collections import Counter
labels = Counter(r.get('ad_classification', '?') for r in records)
print(f'By label: {dict(labels)}')
languages = Counter(r.get('language', '?') for r in records)
print(f'By language: {dict(languages)}')
types = Counter(r.get('content_type', '?') for r in records)
print(f'By type: {dict(types)}')
"
```

Expected: ~300+ records with diverse labels, languages, and content types.

- [ ] **Step 4: Export review queue**

```bash
uv run python -c "
from app.ml.ad_dataset import export_review_queue
export_review_queue(
    '../data/annotated/balanced_ad_training_batch/dataset.jsonl',
    '../data/annotated/balanced_ad_training_batch/review_queue.jsonl'
)
print('Review queue exported')
"
```

Expected: Review queue written.

---

### Task 7: Commit

- [ ] **Step 1: Stage and commit**

```bash
git add backend/app/ml/ad_batch.py backend/app/ml/ad_dataset.py backend/scripts/batch_review.py
git commit -m "feat: add multi-language batch profiles, language field, stratified split, and CLI review helper"
```
