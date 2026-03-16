# AGENTS.md - VeritasAd Development Guide

Guidelines for agentic coding agents working on the VeritasAd project.

## Project Overview

Neural network-based advertising detection system:
- **Frontend**: Next.js 15 (React 19), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.12), SQLAlchemy, PostgreSQL/Redis
- **Infrastructure**: Docker, Celery

---

## Build, Lint, and Test Commands

### Frontend

```bash
cd frontend

npm run dev              # Dev server on 0.0.0.0:3000
npm run build            # Production build
npm run start            # Start production server
npm run lint             # ESLint
npm run type-check       # TypeScript check
```

### Backend

```bash
cd backend
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linting & Formatting
black .                   # Format (line-length: 100)
ruff check .              # Lint
ruff check . --fix        # Fix auto-fixable issues
mypy .                    # Type checking

# Testing
pytest                                    # All tests
pytest tests/unit/                        # Unit tests only
pytest tests/integration/                 # Integration tests
pytest tests/unit/domains/test_x.py        # Single test file
pytest tests/unit/domains/test_x.py::test_fn  # Single test function
pytest --cov=app --cov-report=html        # Coverage report

# Pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Code Style Guidelines

### TypeScript/React (Frontend)

**File Organization:**
- Path aliases: `@/*` → `./src/*`
- Components: `src/components/`, `src/app/` (Next.js App Router)
- Hooks: `src/hooks/`, Utilities: `src/lib/`, Types: `src/types/`

**Naming:**
- Components: PascalCase (`SiteHeader.tsx`, `Button.tsx`)
- Hooks: `use*` prefix (`useKeyboardShortcuts.tsx`)
- Interfaces: PascalCase (`ButtonProps`)
- Multi-export files: lowercase with hyphens (`types/api.ts`)

**Imports:** Use explicit extensions, `type` keyword for type-only imports. Order: React → external → internal → types.

**Patterns:** Use `forwardRef`, functional components with generics, `clsx` + `tailwind-merge` (`cn()`), React Query for server state.

**Styling:** Tailwind CSS v4, CSS variables in globals.css, `dark:` prefix for dark mode.

---

### Python (Backend)

**File Organization:**
- Domain-driven: `app/domains/`
- API routes: `app/api/`, Models: `app/models/`, Schemas: `app/schemas/`
- Services: `app/services/`, Core: `app/core/`

**Naming:**
- Classes: PascalCase (`UserService`)
- Functions/variables: snake_case (`get_user_by_id`)
- Constants: UPPER_SNAKE_CASE
- Private methods: `_` prefix

**Imports (PEP 8):**
```python
# Standard library
import os
from typing import Optional

# Third-party
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

# Local application
from app.models.user import User
```

**Type Hints:** Python 3.12+ syntax, `Optional[X]` over `X | None`, strict mypy enabled.

**Database:** Async SQLAlchemy, Alembic migrations, Pydantic schemas.

**Error Handling:** `HTTPException` for HTTP errors, custom exceptions in `app/core/exceptions.py`, structured logging with `structlog`.

**Testing:** pytest + pytest-asyncio, `tests/unit/` and `tests/integration/`, fixtures in `tests/conftest.py`.

---

## Configuration

**Frontend (.env):** `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Backend (.env):** `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `SUPABASE_*`, `ENVIRONMENT`

**Migrations:**
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

---

## Key Technologies

**Frontend:** Next.js 15, React 19, TypeScript 5.7, Tailwind CSS 4, Supabase, React Query, Recharts, Framer Motion, Lucide React, Sonner

**Backend:** FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Redis, Celery, Alembic, Pydantic v2, Python 3.12

---

## Important Notes

1. No frontend tests configured
2. Strict linting: ESLint (next/core-web-vitals, next/typescript), Black + Ruff
3. Mock auth when Supabase env vars missing
4. Dark mode via next-themes
