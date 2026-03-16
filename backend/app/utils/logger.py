import logging
import sys
from pathlib import Path
from typing import Any, Optional
import structlog
from app.core.config import settings


# Global file handler reference for reuse
_file_handler: Optional[logging.Handler] = None


def _resolve_log_dir() -> Path:
    """Resolve writable log directory with local fallback for dev/tests."""
    preferred = Path(settings.DATA_DIR) / "logs"
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        return preferred
    except PermissionError:
        fallback = Path.cwd() / "logs"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _get_log_file_path() -> Path:
    """Get the log file path based on settings."""
    log_dir = _resolve_log_dir()
    return log_dir / "app.log"


def _create_file_handler() -> logging.Handler:
    """Create and configure a rotating file handler."""
    from logging.handlers import RotatingFileHandler
    
    try:
        log_file = _get_log_file_path()
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
    except PermissionError:
        fallback_file = Path.cwd() / "logs" / "app.log"
        fallback_file.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            fallback_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # File formatter with more details
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def setup_logging() -> None:
    """Configure structured logging with structlog and file output"""
    global _file_handler
    
    # Create file handler
    _file_handler = _create_file_handler()
    
    # Configure stdlib logging with both console and file output
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Add handlers to root logger
    root_logger.addHandler(_file_handler)
    root_logger.addHandler(console_handler)

    # Shared processors for both structlog and stdlib
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Configure structlog
    if settings.LOG_FORMAT == "json":
        # JSON logging for production
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Console dev logging
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Log startup info to file
    logging.getLogger(__name__).info(
        f"Logging initialized. Log file: {_get_log_file_path()}"
    )


def get_logger(name: str) -> Any:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


def get_log_file_path() -> Path:
    """Get the current log file path."""
    return _get_log_file_path() if _file_handler else _get_log_file_path()


def setup_celery_logging() -> None:
    """Configure logging specifically for Celery workers."""
    from logging.handlers import RotatingFileHandler
    
    # Create separate log file for Celery
    log_dir = _resolve_log_dir()
    celery_log_file = log_dir / "celery.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(name)s: %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler for Celery
    try:
        file_handler = RotatingFileHandler(
            celery_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
    except PermissionError:
        fallback_file = Path.cwd() / "logs" / "celery.log"
        fallback_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            fallback_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Configure Celery logger
    celery_logger = logging.getLogger("celery")
    celery_logger.addHandler(file_handler)
    celery_logger.addHandler(console_handler)
    celery_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Log startup info
    logging.getLogger(__name__).info(
        f"Celery logging initialized. Log file: {celery_log_file}"
    )
