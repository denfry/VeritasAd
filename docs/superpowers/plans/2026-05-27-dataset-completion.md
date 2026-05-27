# Dataset Completion — Implementation Plan (Sub-Project B)

**Spec:** `docs/superpowers/specs/2026-05-27-dataset-completion-design.md`
**Executor:** Codex (external) + human reviewer (you)
**Goal:** Deliver 1000 human-reviewed records, locked gold test split, reproducible build, model meeting metric gate.

**Note on human work:** Tasks 4 and 7 require ~10 hours of human review by you. Codex builds the tools; you do the labeling. Tools should be ergonomic enough that 30s/record is realistic.

---

## Task 1 — Extend review_guide.md and dataset schema

**Files:** `data/annotated/balanced_ad_training_batch/review_guide.md` (modify), `backend/app/ml/ad_dataset.py` (modify).

Rewrite `review_guide.md` with concrete examples per label (3–5 each), edge cases (self-promo, charity, government PSA, parody), and a one-screen rubric. Add `gold_test: bool`, `review_round: int`, `suggested_label`, `suggested_confidence`, `review_notes` as optional fields in the record loader. Loader must not break when fields are absent.

**Done when:** existing tests pass; new fields round-trip through `load_records` → `write_jsonl`.

---

## Task 2 — Review-assist tool

**Files (new):** `backend/scripts/dataset_review_assist.py`. **Tests:** `backend/tests/unit/test_review_assist.py`.

CLI:
```
python scripts/dataset_review_assist.py \
  --input ../data/annotated/balanced_ad_training_batch/dataset.jsonl \
  --output ../data/annotated/balanced_ad_training_batch/review_queue.jsonl \
  --model ../models/ad-classifier/hybrid-ad-model.json   # optional
```

For each record with `needs_review = true`, emit a row with: `record_id`, fields the reviewer needs to read (title, transcript, description, urls, disclosure markers), `suggested_label`, `suggested_confidence`, and an empty `review_label`. If model artifact missing, suggestion comes from `compute_analysis_decision` heuristics. Suggestion is informational only.

**Done when:** running the tool produces a queue file; unit test asserts row count matches input and `review_label` is empty.

---

## Task 3 — Review-diff tool for adjudication

**Files (new):** `backend/scripts/dataset_review_diff.py`. **Tests:** `backend/tests/unit/test_review_diff.py`.

Compares two `review_labels.jsonl` files. Emits `disagreements.jsonl` with both labels and an empty `final_label` to be filled by the adjudicator. Prints agreement rate.

**Done when:** unit test on synthetic 100-record input with known overlap returns correct rate and disagreement file.

---

## Task 4 — Human review pass 1 (all 442 existing records)

**Owner:** human reviewer.

1. Run Task 2 tool against current dataset → fills `review_queue.jsonl` with suggestions.
2. Open the queue in your editor of choice (or a simple TUI if Task 5 ships first); fill `review_label` for every record. Skip = `review_label: null` + `review_notes`.
3. Cap sessions at 1 hour. Track time taken.
4. Save as `review_labels.jsonl`.
5. Import: `python scripts/ml_pipeline.py import-labels dataset.jsonl review_labels.jsonl reviewed.jsonl`.

**Done when:** every original record has a non-null `review_label` or is dropped with a note.

---

## Task 5 — Top-up collection profile + mode

**Files:** `backend/scripts/collect_ad_training_batch.py` (modify), `backend/scripts/profiles/balanced_v2.json` (new).

Add `--top-up <reviewed.jsonl>` flag. It counts confirmed labels (not profile hints), computes deficit to reach per-class quota (default 200), and runs collection only for under-quota classes. New profile file `balanced_v2.json` contains improved per-class search queries — especially for `official` (ERID + brand) and `no_ad` (neutral lifestyle / educational sources). Enforce ≤ 5% per-uploader cap during consolidation.

**Tests:** `backend/tests/unit/test_collect_topup.py` — given a mock reviewed file with class counts, deficit computation is correct; per-uploader cap enforced.

**Done when:** dry-run `--top-up` prints planned collection per class with correct deficits.

---

## Task 6 — Run top-up collection

**Owner:** codex + human (cookies for some platforms).

`python scripts/collect_ad_training_batch.py --output-dir ../data/annotated/balanced_ad_training_batch --top-up reviewed.jsonl --run --videos-per-profile 50 --posts-per-profile 50`.

Repeat with adjusted queries until each class has ≥ 200 raw collected (overcollection by 30% to allow for unusable records after review). Commit `dataset.jsonl` after each successful collection pass.

**Done when:** raw collected counts per class ≥ 200 after merging.

---

## Task 7 — Human review pass 2 (new records + gold test split)

**Owner:** human reviewer.

7a. Run Task 2 against newly collected records; review the queue; import labels; merge into `reviewed.jsonl`.

7b. Gold test selection: write a one-off script (`backend/scripts/dataset_gold_select.py`, codex) that stratified-samples 40 records per class from reviewed pool, marks them `gold_test: true` in `dataset.jsonl`, and emits `gold_review_queue.jsonl`. Reviewer (you) does an independent second pass on those 200 — re-label without seeing the first label.

7c. Run Task 3 (`dataset_review_diff`) between original labels and second-pass labels. If disagreement rate > 15%, expand gold pool to 250 and re-sample. Adjudicate disagreements by filling `final_label` in `disagreements.jsonl`; merge back.

**Done when:** 200 gold records marked, second-pass agreement ≥ 85%, all disagreements resolved.

---

## Task 8 — Reproducible build script

**Files (new):** `backend/scripts/dataset_build.py`. `Makefile` target `dataset-build`. **Tests:** `backend/tests/unit/test_dataset_build.py`.

Single command that does:
1. Validate inputs (fail fast if any non-gold record has `needs_review = true`).
2. Carve gold test split from records with `gold_test: true`.
3. Split remaining records into train (85%) and val (15%) using `ml_pipeline.split` with fixed seed.
4. Train using `ml_pipeline.train` with fixed seed.
5. Evaluate on val and gold test.
6. Write `build_<YYYYMMDD>/summary.json` with: input SHA256, per-class counts (overall + per split), metric scores, model seed, dataset fingerprint (SHA256 over sorted `record_id`s), Python + library versions.

Determinism test: run twice → identical summary.json fingerprint and identical split files (byte-for-byte).

**Done when:** determinism test passes; `make dataset-build` produces a model artifact + summary.

---

## Task 9 — Run final build + train + evaluate

**Owner:** codex.

`make dataset-build`. Check `summary.json`:
- Per-class count ≥ 150 in final dataset; gold test ≥ 35/class.
- Val macro-F1 ≥ 0.70 AND test macro-F1 ≥ 0.65 → success, write artifact path to `models/ad-classifier/hybrid-ad-model.json` (overwrite via copy with backup of previous).
- If gate not met: keep build artifact under `build_<date>/`, do not promote, file follow-up note in `docs/decision-log.md` with metrics + suspected causes.

**Done when:** final summary committed; model promoted or follow-up logged.

---

## Task 10 — Docs

**Files:** `docs/ml-ad-detection.md` (modify), `data/annotated/balanced_ad_training_batch/README.md` (new), `docs/decision-log.md` (append).

- `ml-ad-detection.md`: replace ad-hoc instructions with the `make dataset-build` flow; document gold split policy and gate.
- `balanced_ad_training_batch/README.md`: dataset card (size, classes, sources, license note, known limitations, last build date, current model metrics).
- `docs/decision-log.md`: entry documenting the dataset gate decision + outcome.

---

## Verification

- `pytest backend/tests/unit/test_dataset_build.py backend/tests/unit/test_review_assist.py backend/tests/unit/test_review_diff.py backend/tests/unit/test_collect_topup.py` green.
- `make dataset-build` run twice produces identical fingerprints.
- `summary.json` shows all classes ≥ 150, gold ≥ 35/class.
- Either: gate met → new model promoted; or follow-up logged.

## Out of scope

A (local env), C (frontend/UX), model architecture changes, multi-lingual expansion.
