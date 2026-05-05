# Auto-Annotated Dataset

## Totals
- Total records: 88
- Completed: 88
- Failed: 0
- With advertising: 7
- Needs review: 88

## Composition
- post: 80
- video: 8

## Sources
- file: 5
- telegram: 80
- youtube: 3

## Top Brands
- Telegram: 80
- Just: 3
- Проект: 3
- Samsung: 3
- Red Bull: 2
- McLaren: 2
- William Hill: 2
- МАКС: 2
- Самолет: 2
- ПИК: 2
- Начнем: 2
- Европейской: 2
- Это: 2
- Звучит: 2
- Amazon: 2

## Provenance
- Video queries: sponsor promo code discount review, vpn coupon code sponsored review, affiliate link discount code review
- Telegram channels: banksta, meduzalive, rozetked, vcnews, tproger, thevillage, durov
- Generated at output dir: D:\Projects\VeritasAd\data\annotated\auto_dataset_production_seed

## Note
- Labels are model-generated and should be reviewed where confidence is low.

## Ad-Boost Iteration
- Added dataset: `data/annotated/auto_dataset_ad_boost/reviewed_bootstrap.jsonl`
- Combined reviewed dataset: `reviewed_bootstrap_plus_adboost.jsonl`
- Total combined records: 99
- Completed ad-boost records included: 11
- Failed ad-boost records excluded: 1
- Combined labels: `no_ad` 52, `mention` 29, `hidden_ad` 12, `official` 6
- Model artifact: `models/ad-classifier/hybrid-ad-model-production-seed-adboost.json`
- Validation accuracy: 0.5333333333333333
- Test accuracy: 0.7333333333333333
- Decision: not enabled by default. Official examples improved from 1 to 6, but the deterministic source-safe validation/test split has no `official` support yet.
