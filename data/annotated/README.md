Dataset annotation notes

Structure:
- raw: downloaded artifacts per platform
- annotated: Label Studio exports (JSON/CSV)
- processed: cleaned JSONL datasets

Suggested workflow:
1) Collect data using scripts in parsers/
2) Import assets into Label Studio for labeling
3) Export annotations to data/annotated/exports/
4) Normalize to JSONL for training
