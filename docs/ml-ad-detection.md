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

## Runtime Enablement

The model scorer is disabled by default. Enable it with:

```env
AD_MODEL_ENABLED=true
AD_MODEL_ARTIFACT_PATH=../models/ad-classifier/hybrid-ad-model.json
```

If the artifact is missing, invalid, or scoring fails, VeritasAd falls back to the existing deterministic classifier.

## Rollback

Set `AD_MODEL_ENABLED=false` and restart backend/Celery workers. No database migration is required for this first version.
