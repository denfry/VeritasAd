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
