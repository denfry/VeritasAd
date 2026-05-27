# Dataset Completion (Sub-Project B) — Design Spec

**Date:** 2026-05-27
**Sub-project:** B (of A → B → C). A = local env + downloads, C = design/UX.
**Status:** Draft for implementation

## Context

Current state of `data/annotated/balanced_ad_training_batch/`:

- 442 collected records; **all 442 still have `needs_review = true`** — labels are profile hints, not human verdicts.
- Raw class distribution: `mention` 289, `unofficial` 86, `hidden_ad` 46, `no_ad` 12, `official` 9. Severely imbalanced at source.
- `train_ready_balanced_400/` was built by oversampling (28 records duplicated) to 80 per class. Resulting model: val macro-F1 = 0.51, test macro-F1 = 0.51 — unusable.
- Documented production target (`docs/ml-ad-detection.md`): 1k–3k reviewed records.

Root cause of model weakness: not architecture, but **(a)** labels are unverified (profile hints, not gold), and **(b)** real-world `official`/`no_ad` examples are missing — oversampling cannot fix that.

## Goal

Deliver a reproducible 1000-record human-reviewed dataset with a locked gold test split, train an ad classifier that meets a metric gate, and document the build pipeline so anyone can rebuild it from raw sources end-to-end.

## Success Criteria (Definition of Done)

1. ≥ 1000 records in the final dataset; every record has `review_label` set by a human, `needs_review = false`.
2. Per-class minimum 150 records (5 classes × 150 = 750 floor; remaining 250 distributed by natural availability, capped 300/class).
3. Locked gold test split of 200 records, ≥ 35 per class, frozen with a fingerprint hash. Test split is reviewed by two independent passes or one review + adjudication for any disagreement.
4. Reproducible build: `make dataset-build` (or `python scripts/dataset_build.py`) takes raw + review files and produces train/val/test splits, summary, and model artifact deterministically given a seed.
5. Trained model meets gate: val macro-F1 ≥ 0.70 AND test macro-F1 ≥ 0.65. If gate not met, ship the dataset anyway and document a follow-up; do not silently lower the bar.
6. `docs/ml-ad-detection.md` and `data/annotated/balanced_ad_training_batch/README.md` (new) explain the full flow.

## Non-Goals

- Changing model architecture, features, or runtime scoring.
- Improving multimodal pipeline accuracy beyond what the classifier gives.
- Adding new platforms beyond what `collect_ad_training_batch.py` already handles.
- Frontend or UX changes (belongs to C).

## Architecture

Two layers, both data-pipelines, no new runtime services.

### 1. Collection layer

Existing `backend/scripts/collect_ad_training_batch.py`. Extensions:

- New profile config file `backend/scripts/profiles/balanced_v2.json` that targets the gap: aim for 200 `official`, 200 `no_ad`, 200 each of the remaining classes after the existing 442 are reviewed. Profile defines per-class search queries / source URLs.
- `--top-up` mode: reads current reviewed counts, computes deficits, only collects classes still below quota.
- Source diversity guard: cap any single uploader/channel to ≤ 5% of the class to prevent leakage.

### 2. Review layer

Existing `ml_pipeline.py` review flow stays. Additions:

- `scripts/dataset_review_assist.py`: pre-fills `review_label` suggestion using the **current** classifier (`hybrid-ad-model.json` if present, otherwise rule-based fallback from `compute_analysis_decision`). Output JSONL has `suggested_label`, `confidence`, and an empty `review_label` for the human. Suggestion is informational; the reviewer must confirm or override every row.
- `scripts/dataset_review_diff.py`: compares two `review_labels.jsonl` files (for gold split adjudication) and emits disagreements to a third file for resolution.
- Extended `review_guide.md`: concrete examples per label, edge cases (e.g., self-promotion, charity, government PSA), and a 30-second-per-record rubric.

### 3. Build pipeline

New orchestrator script `backend/scripts/dataset_build.py` (or Make target). One command runs:

1. Validate input files exist (`dataset.jsonl`, `review_labels.jsonl`, optional `gold_test_labels.jsonl`).
2. Import labels → `reviewed.jsonl`.
3. If `gold_test_labels.jsonl` exists, carve out the locked test split first (deterministic order: sort by `record_id`, take the gold set).
4. Run `ml_pipeline.py split` on remaining records (val 15%, train 85%).
5. Train model with locked seed; evaluate on val and locked test.
6. Emit `summary.json` with counts, per-class metrics, dataset fingerprint (SHA256 over sorted `record_id`s).

Outputs go under `data/annotated/balanced_ad_training_batch/build_<YYYYMMDD>/`.

## Data Model Additions

`record` in `dataset.jsonl` gains optional fields:

```json
{
  "suggested_label": "official",
  "suggested_confidence": 0.82,
  "review_round": 1,
  "review_notes": "...",
  "gold_test": true
}
```

`gold_test: true` is the marker for the locked test split. It is set once and committed; `dataset_build.py` honors it as the test set source.

## Labeling Policy

- Reviewer fills `review_label` ∈ {`no_ad`, `mention`, `official`, `unofficial`, `hidden_ad`}.
- If a record cannot be judged (broken link, ambiguous), reviewer sets `review_label = null` and `review_notes`. These records are dropped from the final dataset, not labeled.
- Gold test: 200 records selected by stratified sample (40/class) from already-reviewed records, then reviewed independently by a second pass. Disagreements resolved by adjudication; if disagreement rate > 15% on the second pass, expand to 250 and re-sample.
- No `expected_review_label` from the profile is ever copied into `review_label` automatically.

## Reproducibility

- All scripts accept `--seed` (default 20260512, the seed from current artifact).
- Build outputs include `summary.json` with: input file SHA256, label counts, metric scores, model seed, dataset fingerprint, Python + library versions.
- `make dataset-build` is idempotent: re-running with same inputs produces byte-identical splits.

## Testing

- `tests/unit/test_dataset_build.py`: deterministic split → same SHA256 across two runs; gold-test carve-out respects `gold_test: true` markers; deficit calculation correct for `--top-up`.
- `tests/unit/test_review_assist.py`: suggestion script produces a row per input record; empty `review_label`; suggestion present.
- `tests/unit/test_review_diff.py`: agreement / disagreement detection on synthetic inputs.
- Validation rule: build script fails fast if any non-gold record has `needs_review = true`.

## Effort Estimate (Reviewer Time)

This is the realistic part. ~30s/record × 1200 records (1000 final + 200 for second-pass on gold) = 10 hours of focused human review. Spread across multiple sessions. AI-assisted suggestions cut this roughly by half on easy classes (`no_ad`, `official` with explicit ERID).

## Risks

| Risk | Mitigation |
|---|---|
| Reviewer fatigue → label drift | Cap sessions at 1 hour; rubric examples; review_round tracking; sample 5% for self-consistency check |
| Profile collection still skewed | `--top-up` mode + per-uploader cap; manual seeding for `official` (search "ERID + бренд") and `no_ad` (random non-promotional uploads) |
| AI suggestions bias reviewer | Suggestions are shown after first read; UI/CLI displays them in a dimmed field; reviewer must type the label (not click-accept) |
| Gate not met after 1000 records | Ship dataset, log gap, escalate to spec follow-up. Do not lower the gate retroactively |
| Records become stale / sources removed | Snapshot raw text + metadata at collection time (already done in `dataset.jsonl`); don't depend on live URLs at train time |

## Governance Compliance

- `AGENTS.md`: data-only changes; no API or DB migration; runtime model loading already gated by `AD_MODEL_ENABLED`.
- Rollback: previous model artifact remains in `models/ad-classifier/`; switching back is a one-line env change.

## Out of Scope (Explicit)

- Sub-project A (local env / downloads) — separate spec, already drafted.
- Sub-project C (frontend/UX) — separate spec, not yet drafted.
- Multi-lingual expansion of the dataset beyond what's already collected.
- Active-learning loops, RLHF, or LLM-as-judge approaches.
