---
title: Command Reference
created: 2026-05-27
tags: [commands, reference]
status: active
related: ["[[Backend]]", "[[Frontend]]", "[[Release And Governance]]"]
---

# Command Reference

This command reference mirrors the project operating rules and should be checked before local verification.

## Backend

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
alembic revision --autogenerate -m "desc"
alembic upgrade head
uv run pytest
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest --cov=app
```

## Frontend

```bash
npm run dev
npm run build
npm run start
npm run lint
npm run type-check
```

## Formatting And Linting

```bash
uv run black backend/
uv run ruff check backend/
uv run ruff check --fix backend/
uv run mypy backend/app/
cd frontend && npm run lint
pre-commit run --all-files
```

## Related

- [[Backend]]
- [[Frontend]]
- [[Release And Governance]]
