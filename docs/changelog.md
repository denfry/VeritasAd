# Changelog

## Added

- Repository governance operating system documents.
- Architecture current/target maps and scaling strategy docs.
- Release governance, rollback, and upgrade documentation templates.
- Autonomous engineering workflow templates.
- Reviewed-dataset ML utilities for validation, review queue export/import, source-safe splits, training, and evaluation.
- Optional hybrid ad model scorer with rule-based fallback.
- ML workflow documentation in `docs/ml-ad-detection.md`.

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
