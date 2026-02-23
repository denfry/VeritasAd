"""Observability setup - OpenTelemetry tracing and Sentry error tracking."""
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


def init_sentry() -> None:
    """Initialize Sentry for error tracking."""
    if not settings.SENTRY_DSN:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.asyncio import AsyncioIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=settings.VERSION,
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                AsyncioIntegration(),
            ],
        )
        logger.info("sentry_initialized")
    except Exception as e:
        logger.warning("sentry_init_failed", error=str(e))


def init_opentelemetry(app=None) -> None:
    """
    Initialize OpenTelemetry tracing for FastAPI.
    Call with app after create_app() when ENABLE_TRACING is True.
    """
    if not settings.ENABLE_TRACING:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        resource = Resource(attributes={SERVICE_NAME: settings.OTEL_SERVICE_NAME})
        provider = TracerProvider(resource=resource)

        if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
            exporter = OTLPSpanExporter(
                endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces",
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)

        if app is not None:
            FastAPIInstrumentor.instrument_app(app)

        logger.info("opentelemetry_initialized")
    except ImportError as e:
        logger.warning("opentelemetry_not_available", error=str(e))
    except Exception as e:
        logger.warning("opentelemetry_init_failed", error=str(e))
