# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for VeritasAD Bot using UV

# ==================== BUILD STAGE ====================
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependencies only
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# ==================== RUNTIME STAGE ====================
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    mkdir -p /app && \
    chown -R botuser:botuser /app

# Copy the virtualenv from the builder stage
COPY --from=builder --chown=botuser:botuser /app/.venv /app/.venv

# Place the venv on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=botuser:botuser . .

# Switch to non-root user
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run bot
CMD ["python", "main.py"]
