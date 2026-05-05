# ML Ad Detection Workflow

## Purpose

VeritasAd now has a first production-oriented ML foundation for ad classification. It does not replace the multimodal analysis pipeline; it trains a reviewed-dataset classifier on text, metadata, and existing evidence scores, then applies that classifier as an optional scorer.

## Dataset Flow

1. Generate candidate records with `backend/scripts/auto_annotate.py` or another collector that emits JSONL records compatible with existing analysis fields.
2. Validate the dataset:
   ```bash
   cd backend
   python scripts/ml_pipeline.py validate ../data/annotated/<dataset>/dataset.jsonl
   ```
3. Export records that need human review:
   ```bash
   python scripts/ml_pipeline.py export-review ../data/annotated/<dataset>/dataset.jsonl ../data/annotated/<dataset>/review_queue.jsonl
   ```
4. Human reviewers fill `review_label` with one of `no_ad`, `mention`, `official`, `unofficial`, or `hidden_ad`.
5. Import reviewed labels:
   ```bash
   python scripts/ml_pipeline.py import-labels ../data/annotated/<dataset>/dataset.jsonl ../data/annotated/<dataset>/review_labels.jsonl ../data/annotated/<dataset>/reviewed.jsonl
   ```
6. Split without source leakage:
   ```bash
   python scripts/ml_pipeline.py split ../data/annotated/<dataset>/reviewed.jsonl ../data/annotated/<dataset>/splits
   ```

## Balanced Batch Collection

Use `backend/scripts/collect_ad_training_batch.py` to prepare balanced collection batches for the five review labels. By default it creates class-focused profiles for `official`, `hidden_ad`, `unofficial`, `mention`, and `no_ad`.

Dry-run planning writes a manifest and review guide without network collection:

```bash
cd backend
python scripts/collect_ad_training_batch.py --output-dir ../data/annotated/balanced_ad_training_batch --videos-per-profile 10 --posts-per-profile 10
```

Run collection for all profiles:

```bash
python scripts/collect_ad_training_batch.py --output-dir ../data/annotated/balanced_ad_training_batch --videos-per-profile 10 --posts-per-profile 10 --run
```

If profile folders already exist, rebuild the combined dataset and review queue only:

```bash
python scripts/collect_ad_training_batch.py --output-dir ../data/annotated/balanced_ad_training_batch --consolidate-only
```

The generated `review_queue.jsonl` includes `expected_review_label` as a reviewer hint only. Human reviewers must still fill `review_label`; do not treat profile targets as gold labels.

## Training and Evaluation

Train a model artifact:

```bash
cd backend
python scripts/ml_pipeline.py train ../data/annotated/<dataset>/splits/train.jsonl ../models/ad-classifier/hybrid-ad-model.json --eval ../data/annotated/<dataset>/splits/val.jsonl
```

Evaluate against the locked reviewed test split:

```bash
python scripts/ml_pipeline.py evaluate ../models/ad-classifier/hybrid-ad-model.json ../data/annotated/<dataset>/splits/test.jsonl
```

The first production target is 1k-3k reviewed examples. The golden test split must be manually reviewed before metrics are accepted.

## Seed Artifacts

Current checked-in seed artifacts are intentionally disabled by default:

- `models/ad-classifier/hybrid-ad-model-production-seed.json` was trained from 88 bootstrap-reviewed records.
- `models/ad-classifier/hybrid-ad-model-production-seed-adboost.json` adds 11 successful targeted YouTube advertising examples and excludes 1 failed m3u8 download.

The ad-boost artifact uses 99 records total with labels: `no_ad` 52, `mention` 29, `hidden_ad` 12, `official` 6. Its validation accuracy is 0.5333333333333333 and test accuracy is 0.7333333333333333, but the deterministic source-safe validation/test split has no `official` support yet, so it is retained only as an iteration artifact and must not be enabled as the default production model.

## Runtime Enablement

The model scorer is disabled by default. Enable it with:

```env
AD_MODEL_ENABLED=true
AD_MODEL_ARTIFACT_PATH=../models/ad-classifier/hybrid-ad-model.json
```

If the artifact is missing, invalid, or scoring fails, VeritasAd falls back to the existing deterministic classifier.

## Rollback

Set `AD_MODEL_ENABLED=false` and restart backend/Celery workers. No database migration is required for this first version.
