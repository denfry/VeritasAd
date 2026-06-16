# VeritasAd Research Tooling

Distant-supervision corpus tooling for the master's/PhD research program
(see `../docs/research/2026-06-16-veritasad-research-roadmap.md`).

This package is intentionally **decoupled** from the production backend: it has
light dependencies (`yt-dlp` + stdlib) so the corpus can be rebuilt reproducibly
without the full ML stack.

## Setup

```bash
cd research
uv sync
```

## Build a corpus

```bash
uv run python -m corpus.cli \
  --sources data/sources.example.jsonl \
  --manifest data/manifest.jsonl
```

The run is **resumable**: already-harvested video IDs are skipped, so you can
extend `sources` and re-run. A failed fetch logs `[skip] ...` and does not abort
the harvest. The command prints label/platform statistics on completion.

## What it produces

A JSONL manifest of weak labels:
- `disclosed_ad` — a strong regulatory marker (ERID, advertiser INN, #реклама,
  "на правах рекламы") was found → trusted positive for distant supervision.
- `unlabeled` — no strong marker → clean **or** hidden ad (resolved later by the
  model and the manually annotated gold test set).

## Tests

```bash
uv run pytest
```
