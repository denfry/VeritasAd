# Decision Log

## 2026-04-08 - Governance System Bootstrapped

- Established a repository operating system with mandatory docs and workflows.
- Chose modular monolith evolution over immediate service decomposition.
- Prioritized behavior preservation and rollback-first release safety.
- Adopted recurring-issue to rule/workflow/checklist conversion model.

## 2026-05-05 - Hybrid Reviewed-Dataset Classifier

- Chose a hybrid text + evidence-feature classifier for the first production ML version.
- Kept the current rule-based classifier as the default runtime path and fallback.
- Deferred full multimodal fine-tuning until a larger reviewed dataset and locked golden test set exist.
- Avoided a database migration in v1; model metadata is returned on immediate responses where available.

## 2026-05-05 - Balanced Ad Batch Collection

- Added a class-focused batch planner before expanding training data further.
- Treat profile labels as reviewer hints only; gold labels must still come from manual review.
- Keep collection orchestration separate from `auto_annotate.py` so the existing collector remains backward compatible.

## 2026-06-17 - Research Workspace Structure

- Consolidated scattered research artifacts into a single extensible tree `docs/research/`, organized **by artifact type** (roadmaps / prompts / plans / specs / reports / experiments / datasets / literature), each split into `master/` (2.0) and `phd/` (3.0) phases.
- Migrated existing artifacts via `git mv` (history preserved): M2 spec, shared system prompts, and the related-work review; moved the two roadmaps into `roadmaps/`.
- Fixed conventions in [`docs/research/README.md`](research/README.md): naming (`YYYY-MM-DD-<milestone>-<slug>.md`), YAML frontmatter, status lifecycle (`planned → draft → in-review → approved → done`), milestone map, and a path-correspondence table mapping the roadmaps' flat `docs/*.md` names to the new locations.
- Kept dataset **documentation** (`docs/research/datasets/`) separate from the **data** (`data/datasets/`, with raw/large files git-ignored).
- Left `GEMINI.md` in the repository root (Gemini CLI context file, read from root — moving it would break behavior).

## 2026-06-17 - Claim Extraction MVP (VeritasAd 2.0, M2)

- Added claim extraction as a new domain `app/domains/claims` (router/service/dependencies) plus dedicated services (`claim_extractor`, `claim_normalizer`, `claim_classifier`, `checkworthiness_scorer`, `claim_fewshot`, `claim_export`) and pydantic schemas, rather than folding the logic into the existing analysis path — keeps the new subsystem isolated and independently testable.
- Integrated extraction **on-demand behind `CLAIM_EXTRACTION_ENABLED=false`** (method via `CLAIM_EXTRACTION_METHOD`, default `rule_based`); the pipeline hook is wrapped in try/except and never fails the analysis task. Rationale: `AGENTS.md` preserve-behavior — the default runtime path is unchanged.
- Persisted results via an **additive, nullable `analyses.claims` (JSONB/JSON) column** with reversible Alembic migration `015_add_analysis_claims` (SQLite synchronized) instead of a new table, so existing rows and serializers stay valid; the `claims` payload is also surfaced in `GET /api/v1/analysis/{task_id}/result`.
- Chose `rule_based` as the **default offline method** (no API keys, reproducible), with optional LLM zero-shot / few-shot extraction routed through the unified `llm_service` (honours `MOCK_LLM_RESPONSES`) and falling back to `rule_based` when the LLM is unavailable. Rationale: reproducibility for thesis experiments and no hard dependency on external LLM access.
- **Rollback:** set `CLAIM_EXTRACTION_ENABLED=false` to drop extraction from the pipeline (endpoints remain on-demand); run `alembic downgrade -1` to drop the additive `analyses.claims` column.
