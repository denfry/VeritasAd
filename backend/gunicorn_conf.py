"""Gunicorn configuration for production deployment."""
import multiprocessing
import os

# Server socket
_port = os.getenv("PORT", "8000")
bind = os.getenv("GUNICORN_BIND", f"0.0.0.0:{_port}")

# Worker processes: CPU count * 2 + 1 for I/O-bound FastAPI, capped at 4 for containers
_default_workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
workers = int(os.getenv("GUNICORN_WORKERS", _default_workers))
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Process naming
proc_name = "veritasad-api"

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Keepalive
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
