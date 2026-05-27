# Language Switcher + Dataset Completion — Design Spec

**Date:** 2026-05-14
**Author:** opencode
**Status:** Draft

---

## 1. Language System (Frontend)

### 1.1 `frontend/src/lib/languages.ts`

New file — a mapping every `ALL_CURRENCIES` entry → a primary language.

```ts
interface Language {
  code: string          // ISO 639-1 (ru, en, zh, ar, hi, ja, etc.)
  name: string          // English name ("Russian", "English")
  nativeName: string    // Native name ("Русский", "English")
  flag: string          // Emoji flag — reuse from currency (🇷🇺, 🇺🇸)
}
```

One record per currency, picking the most common/official language for that country/region.

| Currency | Language code | name          | nativeName     | flag  |
|----------|--------------|---------------|----------------|-------|
| RUB      | ru           | Russian       | Русский        | 🇷🇺  |
| USD      | en           | English       | English        | 🇺🇸  |
| EUR      | en           | English       | English        | 🇪🇺  |
| GBP      | en           | English       | English        | 🇬🇧  |
| CNY      | zh           | Chinese       | 中文           | 🇨🇳  |
| JPY      | ja           | Japanese      | 日本語         | 🇯🇵  |
| KRW      | ko           | Korean        | 한국어         | 🇰🇷  |
| KZT      | kk           | Kazakh        | Қазақша        | 🇰🇿  |
| BYN      | be           | Belarusian    | Беларуская     | 🇧🇾  |
| UAH      | uk           | Ukrainian     | Українська     | 🇺🇦  |
| TRY      | tr           | Turkish       | Türkçe         | 🇹🇷  |
| INR      | hi           | Hindi         | हिन्दी         | 🇮🇳  |
| AED      | ar           | Arabic        | العربية        | 🇦🇪  |
| …        |              |               |                |      |

~150 entries matching the currency list.

Exports:
- `ALL_LANGUAGES: Language[]`
- `POPULAR_LANGUAGES: Language[]` (subset for quick access, same 12 as popular currencies)
- `getLanguageByCode(code: string): Language | undefined`

### 1.2 LanguageContext (`frontend/src/contexts/language-context.tsx`)

Analogous to `CurrencyContext`:

- Stores selected language code (initially `"ru"`)
- Persists to localStorage key `veritasad_selected_language`
- Fetches/syncs with `/api/user/preferences` → `language` field
- Provides:
  - `language: string` (current code)
  - `setLanguage: (code: string) => void`
  - `allLanguages: Language[]`

### 1.3 LanguageSelector Component (`frontend/src/components/LanguageSelector.tsx`)

Reuses the `CurrencySelector` UI pattern:

- Trigger button: flag + language code, chevron
- Dropdown:
  - Search bar (filters by code / name / nativeName)
  - Popular section (top 6)
  - All section
- On select → calls `setLanguage()`, closes dropdown

### 1.4 SiteHeader Integration

Add `LanguageSelector` next to `CurrencySelector` in `SiteHeader.tsx`:

```
[Logo] [Nav] ... [LanguageSelector] [CurrencySelector] [UserMenu]
```

### 1.5 Settings Page Update

In `frontend/src/app/(app)/dashboard/settings/page.tsx`:

- Replace hardcoded `languages` array with dynamic import from `lib/languages`
- Keep the same 2-column grid layout
- Use cursor-based styling for larger list

### 1.6 No i18n / translation system

This iteration adds only the **switcher** and **data model**. Full UI translation (next-intl, etc.) is out of scope.

---

## 2. Dataset Completion (Backend)

### 2.1 Language-enriched Batch Profiles

Extend `BatchProfile` in `ad_batch.py` with a `language` field:

```python
@dataclass(frozen=True)
class BatchProfile:
    name: str
    language: str  # ISO 639-1 — new field
    expected_label: str
    video_queries: tuple[str, ...]
    telegram_channels: tuple[str, ...] = ()
    reviewer_hint: str = ""
```

Add new language-specific profiles to `DEFAULT_BATCH_PROFILES`:

| Profile     | Language | Expected Label | Video Queries (examples)               | Telegram Channels                     |
|-------------|----------|----------------|----------------------------------------|---------------------------------------|
| official_en | en       | official       | "sponsored use promo code review"      | durov                                 |
| hidden_en   | en       | hidden_ad      | "affiliate link discount no disclosure"| durov                                 |
| mention_en  | en       | mention        | "tech review unboxing comparison"      | durov                                 |
| no_ad_en    | en       | no_ad          | "tutorial building project"            | durov, tproger                        |
| official_zh | zh       | official       | "赞助 推广 优惠码 评测"                  | (YouTube only)                        |
| hidden_zh   | zh       | hidden_ad      | "联盟营销 折扣码 评测"                   | (YouTube only)                        |
| mention_zh  | zh       | mention        | "开箱 评测 对比"                        | (YouTube only)                        |
| no_ad_zh    | zh       | no_ad          | "教程 新闻 分析"                        | (YouTube only)                        |
| …_es        | es       | …              | "código descuento patrocinado reseña"  | (YouTube + Telegram)                  |
| …_ar        | ar       | …              | "رمز ترويجي مراجعة رعاية"              | (YouTube + Telegram)                  |
| …_hi        | hi       | …              | "प्रायोजित समीक्षा प्रोमो कोड"          | (YouTube + Telegram)                  |

Each language group mirrors the 5-label structure (official, hidden_ad, unofficial, mention, no_ad).

### 2.2 Pipeline Changes

**`ad_dataset.py`:**
- Add `language: str` field to `NormalizedAdRecord`
- Extract language from `batch_profile` field or auto-detect from text content
- Export language in feature dict

**Split logic (`split_records`):**
- Stratify by `(label, source_type, language)` to ensure every language appears in train/val/test
- Update test to verify no language is missing from any split

### 2.3 Collection Run

Execute:

```bash
cd backend
python scripts/collect_ad_training_batch.py \
  --videos-per-profile=30 \
  --posts-per-profile=30 \
  --run
```

Target: **300–500** total records (vs current 88).

### 2.4 Review Workflow

1. **Export review queue** → `review_queue.jsonl` (already implemented in `ad_dataset.py:export_review_queue`)
2. **CLI review helper** — new script `scripts/batch_review.py`:
   - Loads review queue
   - Presents each record one-at-a-time
   - Accepts keyboard shortcuts for each label class
   - Writes to `review_labels.jsonl` incrementally
3. **Import labels** → `python scripts/ml_pipeline.py import-labels ...` (or cons old) → produces `reviewed.jsonl`
4. **Re-split & retrain** → auto-evaluate on test set

### 2.5 Artifacts

Output directory: `data/annotated/balanced_ad_training_batch/` with:
- `dataset.jsonl` — all records
- `review_queue.jsonl` — for manual review
- `review_labels.jsonl` — reviewed labels (filled incrementally)
- `reviewed.jsonl` — final merged dataset
- `splits/` — train/val/test (per label + language stratification)
- `summary.md` — counts by label, language, source_type, accuracy

---

## 3. File Changes Summary

| File | Action |
|------|--------|
| `frontend/src/lib/languages.ts` | **Create** — Language map ~150 entries |
| `frontend/src/contexts/language-context.tsx` | **Create** — LanguageContext + Provider |
| `frontend/src/components/LanguageSelector.tsx` | **Create** — Dropdown selector |
| `frontend/src/components/SiteHeader.tsx` | **Edit** — Add LanguageSelector |
| `frontend/src/app/providers.tsx` | **Edit** — Wrap LanguageProvider |
| `frontend/src/app/(app)/dashboard/settings/page.tsx` | **Edit** — Dynamic languages |
| `backend/app/ml/ad_batch.py` | **Edit** — Add language field + profiles |
| `backend/app/ml/ad_dataset.py` | **Edit** — Add language to NormalizedAdRecord + stratified split |
| `backend/scripts/collect_ad_training_batch.py` | **Edit** — Pass language param if needed |
| `backend/scripts/batch_review.py` | **Create** — CLI review helper |

---

## 4. Out of Scope

- Full i18n/translation of the UI (only switcher infrastructure)
- Label Studio integration (manual review stays CLI-based for now)
- Model re-training or deployment (dataset creation only)
