# Ad Training Batch Review Guide

## Labels
- `official`: paid promotion with explicit disclosure such as `#ad`, `#sponsored`, ERID, or paid partnership.
- `hidden_ad`: commercial CTA, affiliate/coupon link, or sales script without clear disclosure.
- `unofficial`: likely advertising or endorsement, but without enough evidence for official or hidden advertising.
- `mention`: brand mention or review without clear promotional intent.
- `no_ad`: no meaningful ad signal.

## Profile Hints
- `official` expects `official`: Paid promotion with an explicit disclosure marker such as #ad, #sponsored, ERID, or paid partnership.
- `hidden_ad` expects `hidden_ad`: Commercial CTA, affiliate/coupon link, or sales script without clear disclosure.
- `unofficial` expects `unofficial`: Advertising intent is plausible, but official disclosure and hard affiliate evidence are absent.
- `mention` expects `mention`: Brand appears or is discussed, but the content is not primarily promotional.
- `no_ad` expects `no_ad`: No meaningful brand promotion, CTA, disclosure, or commercial link evidence.

## Review Flow
1. Fill `review_labels.jsonl` with JSONL rows: `record_id`, `review_label`, and optional `notes`.
2. Import labels after review:
   ```bash
   python scripts/ml_pipeline.py import-labels data\annotated\balanced_ad_training_batch\dataset.jsonl data\annotated\balanced_ad_training_batch\review_labels.jsonl data\annotated\balanced_ad_training_batch\reviewed.jsonl
   ```
3. Split, train, and evaluate only after the reviewed labels are complete.
