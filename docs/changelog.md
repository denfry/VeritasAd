# Changelog

## VeritasAd 2.0 — M2: Claim Extraction MVP — 2026-06-17

### Added

- Claim-extraction subsystem: verifiable advertising claims are extracted from the multimodal signals (ASR, OCR, metadata, brands, disclosure markers, CTA, links), normalized, classified by an 11-class taxonomy, risk-scored, and checkworthiness-scored.
- Pydantic schemas `Claim` / `ClaimExtractionRequest` / `ClaimExtractionResult` with enums `ClaimType` (11), `RiskLevel` (4), `SourceModality` (5), `ExtractionMethod` (`rule_based` / `llm_zero_shot` / `llm_few_shot`).
- Services: `claim_extractor` (orchestrator), `claim_normalizer`, `claim_classifier`, `checkworthiness_scorer`, `claim_fewshot` (zero/few-shot prompts), `claim_export` (JSONL/CSV).
- New `app/domains/claims` domain with API endpoints: `POST /api/v1/claims/extract`, `POST /api/v1/claims/from-analysis/{task_id}`, `GET /api/v1/claims/{task_id}`, `GET /api/v1/claims/{task_id}/export?format=jsonl|csv`.
- JSONL/CSV export of extracted claims in the dataset row format (`docs/research/datasets/claims/schema.md`).
- Frontend claims view: `ClaimsTable`, `ClaimDetailsCard`, `ClaimRiskBadge`, `ClaimTimeline`, a claims section on the analysis page, API client, TS types, and ru/en i18n strings.
- Research prompt artifact `docs/research/prompts/master/claim-extraction.md` documenting the zero-shot and few-shot extraction prompts.

### Changed

- On-demand claim extraction is integrated into the analysis pipeline behind the feature flag `CLAIM_EXTRACTION_ENABLED` (off by default; method via `CLAIM_EXTRACTION_METHOD`, default `rule_based` — offline, no API keys), preserving existing analysis behavior.
- Analysis serialization now carries an optional `claims` payload (a `ClaimExtractionResult` or `null`) in `GET /api/v1/analysis/{task_id}/result`.
- LLM zero/few-shot extraction routes through the unified `llm_service` and honours `MOCK_LLM_RESPONSES` in development.

### Migration Notes

- Additive, reversible Alembic migration `015_add_analysis_claims` introduces a nullable `analyses.claims` (JSONB/JSON) column; SQLite schema synchronized.
- Runtime behavior is unchanged unless `CLAIM_EXTRACTION_ENABLED=true`.

### Rollback Notes

- Disable `CLAIM_EXTRACTION_ENABLED` to remove claim extraction from the pipeline (endpoints remain available on-demand).
- `alembic downgrade -1` drops the additive `analyses.claims` column.

## Added

- Repository governance operating system documents.
- Architecture current/target maps and scaling strategy docs.
- Release governance, rollback, and upgrade documentation templates.
- Autonomous engineering workflow templates.
- Reviewed-dataset ML utilities for validation, review queue export/import, source-safe splits, training, and evaluation.
- Optional hybrid ad model scorer with rule-based fallback.
- ML workflow documentation in `docs/ml-ad-detection.md`.
- Targeted ad-boost seed dataset and disabled iteration model artifact for official advertising examples.
- Balanced ad-training batch planner for class-focused collection and manual review queue preparation.

## Changed

- `AGENTS.md` expanded into mandatory governance contract.
- Analysis responses can include optional model metadata fields when `AD_MODEL_ENABLED=true`.

## Migration Notes

- No database migration is required for the ML scorer foundation.
- Runtime behavior is unchanged unless `AD_MODEL_ENABLED=true` and `AD_MODEL_ARTIFACT_PATH` points to a valid artifact.
- Governance docs are now required references for future tasks.

## Rollback Notes

- Revert docs and AGENTS changes if governance adoption must be postponed.
- Disable `AD_MODEL_ENABLED` to return all analysis decisions to the deterministic classifier.
