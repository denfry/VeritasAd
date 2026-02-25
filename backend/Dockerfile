# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for VeritasAD Backend - Production using UV

# ==================== BUILD STAGE ====================
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy dependencies only to leverage caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen ensures we use the exact versions from uv.lock
RUN uv sync --frozen --no-dev --no-install-project

# ==================== RUNTIME STAGE ====================
FROM python:3.12-slim

# Install ONLY runtime dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 veritasad && \
    mkdir -p /app /app/data /app/models && \
    chown -R veritasad:veritasad /app

WORKDIR /app

# Copy the virtualenv from the builder stage
COPY --from=builder --chown=veritasad:veritasad /app/.venv /app/.venv

# Place the venv on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=veritasad:veritasad . .

# Switch to non-root user
USER veritasad

# Create necessary directories
RUN mkdir -p \
    /app/data/raw \
    /app/data/processed \
    /app/data/reports \
    /app/data/temp \
    /app/data/uploads \
    /app/models/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command: Gunicorn + Uvicorn workers for production
CMD ["gunicorn", "app.main:app", "-c", "gunicorn_conf.py"]
