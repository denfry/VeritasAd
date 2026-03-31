# AGENTS.md — VeritasAd

Neural network-based advertising detection system. FastAPI backend + Next.js 15 frontend.

## Commands

### Frontend (`frontend/`)

```bash
npm run dev          # Dev server on 0.0.0.0:3000
npm run build        # Production build
npm run start        # Start production server
npm run lint         # ESLint (next lint)
npm run type-check   # TypeScript check (next build --no-lint)
```

No test runner is configured for the frontend.

### Backend (`backend/`)

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  # Dev server
alembic revision --autogenerate -m "desc"                         # New migration
alembic upgrade head                                              # Apply migrations
```

### Backend Tests

```bash
uv run pytest                          # Run all tests
uv run pytest tests/test_api.py        # Run single test file
uv run pytest tests/unit/              # Run unit tests only
uv run pytest tests/integration/       # Run integration tests only
uv run pytest -k "test_something"      # Run test by name substring
uv run pytest tests/test_api.py::test_function_name  # Run single test
uv run pytest --cov=app                # Run with coverage
```

Tests use pytest + pytest-asyncio (auto mode), in-memory SQLite. Fixtures in `tests/conftest.py`.

### Linting & Formatting

```bash
# Backend
uv run black backend/
uv run ruff check backend/
uv run ruff check --fix backend/
uv run mypy backend/app/

# Frontend
cd frontend && npm run lint

# Pre-commit (runs all hooks)
pre-commit run --all-files
```

## Code Style

### TypeScript / React (Frontend)

- **Strict TypeScript** (`strict: true`, ES2022 target, `noEmit: true`)
- **Path alias**: `@/*` maps to `./src/*`
- **Components**: PascalCase (`UploadPanel.tsx`), placed in `src/components/`
- **Hooks**: camelCase, prefixed with `use` (`useAnalysis.ts`)
- **Pages**: Next.js App Router in `src/app/`, kebab-case route segments
- **Imports**: Absolute paths via `@/` alias. Group: React/next, third-party, internal
- **Styling**: Tailwind CSS v4 with `clsx` + `tailwind-merge` via `cn()` utility
- **Dark mode**: `class` strategy via `next-themes`
- **State**: TanStack React Query for server state, React state for UI state
- **ESLint**: `next/core-web-vitals` + `next/typescript`

### Python (Backend)

- **Line length**: 100 (Black + Ruff)
- **Formatting**: Black (auto-formatted), Ruff for linting
- **Ruff rules**: `E, F, I, N, W, UP` (auto-import sorting via `I`)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Type hints**: Required on function signatures. `disallow_untyped_defs = false` but `check_untyped_defs = true`
- **Imports**: Standard lib, third-party, local — separated by blank lines (Ruff `I` handles this)
- **Database**: SQLAlchemy 2.0 async, models in `backend/app/models/`
- **Schemas**: Pydantic v2 in `backend/app/schemas/`
- **Routes**: FastAPI routers in `backend/app/api/`
- **Business logic**: Domain-driven in `backend/app/domains/`
- **Error handling**: Custom exceptions in `core/exceptions.py`, HTTPException for API errors
- **Logging**: `structlog` for structured logging
- **Async**: Use `async def` for I/O-bound handlers; pytest-asyncio `auto` mode

## Project Structure

```
backend/app/          # FastAPI app
  api/                # Route definitions
  core/               # Config, exceptions, security
  domains/            # Business logic
  models/             # SQLAlchemy models
  schemas/            # Pydantic schemas
  services/           # Service layer
  tasks/              # Celery background tasks

frontend/src/
  app/                # Next.js App Router pages
  components/         # React components
  contexts/           # React contexts
  hooks/              # Custom hooks
  lib/                # Utilities
  types/              # TypeScript types
```

## Key Notes

- Package manager: **uv** for backend (uses `uv.lock`), **npm** for frontend
- Python 3.12 required (`>=3.12,<3.13`)
- Auth via Supabase (frontend) + python-jose/PyJWT (backend)
- Celery + Redis for background tasks
- ML stack: PyTorch, Transformers, faster-whisper, librosa, OpenCV
- Observability: OpenTelemetry + Sentry + structlog
- All modules (admin, analytics, billing, bot) are placeholders
