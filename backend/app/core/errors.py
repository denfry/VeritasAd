from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class ErrorCode:
    """Error codes for API responses"""
    
    # General
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    
    # Auth
    INVALID_API_KEY = "INVALID_API_KEY"
    API_KEY_REQUIRED = "API_KEY_REQUIRED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    ACCOUNT_BANNED = "ACCOUNT_BANNED"
    
    # Video processing
    VIDEO_TOO_LARGE = "VIDEO_TOO_LARGE"
    VIDEO_TOO_LONG = "VIDEO_TOO_LONG"
    INVALID_VIDEO_FORMAT = "INVALID_VIDEO_FORMAT"
    VIDEO_DOWNLOAD_FAILED = "VIDEO_DOWNLOAD_FAILED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    
    # Resources
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    REPORT_NOT_FOUND = "REPORT_NOT_FOUND"


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class VeritasAdException(Exception):
    """Base exception for VeritasAd API"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class ValidationException(VeritasAdException):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class NotFoundException(VeritasAdException):
    """Resource not found"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.NOT_FOUND):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AuthException(VeritasAdException):
    """Authentication/Authorization error"""
    
    def __init__(
        self,
        message: str,
        error_code: str = ErrorCode.INVALID_API_KEY,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class RateLimitException(VeritasAdException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


class VideoProcessingException(VeritasAdException):
    """Video processing error"""
    
    def __init__(self, message: str, error_code: str = ErrorCode.PROCESSING_FAILED):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def veritasad_exception_handler(
    request: Request, exc: VeritasAdException
) -> JSONResponse:
    """Handle custom VeritasAd exceptions"""
    logger.warning(
        "api_error",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            details={"errors": exc.errors()},
        ).model_dump(),
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    logger.warning(
        "http_error",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTPException",
            error_code="HTTP_ERROR",
            message=str(exc.detail),
        ).model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    logger.exception(
        "unexpected_error",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=type(exc).__name__,
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An internal error occurred. Please try again later.",
        ).model_dump(),
    )
