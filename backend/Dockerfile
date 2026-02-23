# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for VeritasAD Backend - Production

# ==================== BUILD STAGE ====================
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependencies file
COPY pyproject.toml ./
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
        --default-timeout=1000 \
        --retries=10 \
        -r requirements.txt

# ==================== RUNTIME STAGE ====================
FROM python:3.11-slim

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

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code (исключая .dockerignore)
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
