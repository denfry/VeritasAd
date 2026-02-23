from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import Header, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import structlog
import jwt
from jwt import PyJWTError
import json
import time
import hashlib
import requests

from app.core.config import settings
from app.core.errors import AuthException, RateLimitException
from app.models.database import get_db, User, UserPlan, UserRole

logger = structlog.get_logger(__name__)

security = HTTPBearer(auto_error=False)

_JWKS_CACHE: Dict[str, Any] = {"fetched_at": 0, "keys": []}
_JWKS_TTL_SECONDS = 60 * 60  # 1 hour cache


def hash_api_key(api_key: str) -> str:
    """
    Hash API key using SHA-256 for secure storage and lookup.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def _get_supabase_jwks() -> List[Dict[str, Any]]:
    if not settings.SUPABASE_URL:
        return []

    now = time.time()
    if _JWKS_CACHE["keys"] and now - _JWKS_CACHE["fetched_at"] < _JWKS_TTL_SECONDS:
        return _JWKS_CACHE["keys"]

    try:
        headers = {}
        if settings.SUPABASE_ANON_KEY:
            headers["Authorization"] = f"Bearer {settings.SUPABASE_ANON_KEY}"
            headers["apikey"] = settings.SUPABASE_ANON_KEY

        response = requests.get(
            f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json",
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        jwks = response.json()
        keys = jwks.get("keys", [])
        _JWKS_CACHE["keys"] = keys
        _JWKS_CACHE["fetched_at"] = now
        return keys
    except Exception as exc:
        logger.warning("jwks_fetch_failed", error=str(exc))
        return []


def _get_public_key_from_jwk(jwk: Dict[str, Any], alg: str):
    jwk_json = json.dumps(jwk)
    if alg.startswith("ES"):
        return jwt.algorithms.ECAlgorithm.from_jwk(jwk_json)
    if alg.startswith("RS"):
        return jwt.algorithms.RSAAlgorithm.from_jwk(jwk_json)
    raise AuthException(
        message=f"Unsupported JWT algorithm: {alg}",
        error_code="UNSUPPORTED_JWT_ALG",
    )


async def verify_supabase_token(token: str) -> dict:
    """
    Verify Supabase JWT token and return payload.
    Includes explicit validation of exp, nbf, iat claims.

    For local development (when SUPABASE_URL is not set),
    decodes JWT without signature verification (dev only).
    """
    if not settings.SUPABASE_JWT_SECRET and not settings.SUPABASE_URL:
        # Local development mode - decode without signature verification
        logger.info("Using local JWT verification mode (Supabase not configured)")
        try:
            # Decode without signature verification for local dev
            # This is safe because it's only enabled when Supabase is not configured
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "require": ["exp", "iat", "sub"],
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                },
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthException(
                message="Token has expired",
                error_code="TOKEN_EXPIRED",
            )
        except PyJWTError as exc:
            logger.warning("local_jwt_decode_failed", error=str(exc))
            raise AuthException(
                message="Invalid token format",
                error_code="INVALID_TOKEN",
            )
        except Exception as exc:
            logger.error("local_jwt_verification_error", error=str(exc))
            raise AuthException(
                message="Token verification failed",
                error_code="INVALID_TOKEN",
            )

    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")
        
        # Validate algorithm - only allow secure algorithms
        if alg not in ["HS256", "RS256", "ES256"]:
            raise AuthException(
                message=f"Unsupported JWT algorithm: {alg}",
                error_code="UNSUPPORTED_JWT_ALG",
            )

        if settings.SUPABASE_JWT_SECRET:
            try:
                # Explicitly require and verify critical claims
                return jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    audience="authenticated",
                    options={
                        "require": ["exp", "iat", "sub"],
                        "verify_exp": True,
                        "verify_nbf": True,
                        "verify_iat": True,
                        "verify_aud": True,
                    },
                )
            except PyJWTError as exc:
                logger.warning("jwt_hs256_verification_failed", error=str(exc))
                raise AuthException(
                    message="Invalid or expired token",
                    error_code="INVALID_TOKEN",
                )

        keys = _get_supabase_jwks()
        if keys:
            kid = header.get("kid")
            for jwk_key in keys:
                if not kid or jwk_key.get("kid") == kid:
                    public_key = _get_public_key_from_jwk(jwk_key, alg)
                    return jwt.decode(
                        token,
                        public_key,
                        algorithms=[alg],
                        audience="authenticated",
                        options={
                            "require": ["exp", "iat", "sub"],
                            "verify_exp": True,
                            "verify_nbf": True,
                            "verify_iat": True,
                            "verify_aud": True,
                        },
                    )

        raise AuthException(
            message="Supabase token verification failed",
            error_code="INVALID_TOKEN",
        )
    except AuthException:
        raise
    except PyJWTError as e:
        logger.warning("jwt_verification_failed", error=str(e))
        raise AuthException(
            message="Invalid or expired token",
            error_code="INVALID_TOKEN",
        )
    except Exception as e:
        logger.error("token_verification_error", error=str(e))
        raise AuthException(
            message="Token verification failed",
            error_code="INVALID_TOKEN",
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate authentication (JWT or API key) and return current user.
    Supports both Supabase JWT (preferred) and legacy API key.
    Automatically creates new user if needed.
    Checks rate limits and account status.

    API keys are hashed before database lookup for security.

    When DISABLE_AUTH=True (development only), returns a mock admin user
    to allow testing without authentication.
    """
    # Development mode: disable authentication for testing
    if settings.DISABLE_AUTH:
        logger.warning("Authentication is DISABLED. Using mock admin user.")
        # Create a mock admin user for testing
        mock_user = User(
            id=0,
            email="test@veritasad.ai",
            plan=UserPlan.ENTERPRISE,
            role=UserRole.ADMIN,
            daily_limit=999999,
            daily_used=0,
            is_active=True,
            is_banned=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        return mock_user

    user = None

    # Try JWT first (Supabase)
    auth_token = None
    if credentials and credentials.credentials:
        auth_token = credentials.credentials
    elif token:
        auth_token = token

    if auth_token:
        try:
            payload = await verify_supabase_token(auth_token)
            supabase_user_id = payload.get("sub")
            email = payload.get("email")

            if not supabase_user_id:
                raise AuthException(
                    message="Invalid token payload",
                    error_code="INVALID_TOKEN_PAYLOAD",
                )

            # Get or create user by supabase_user_id
            result = await db.execute(
                select(User).where(User.supabase_user_id == supabase_user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                # Auto-create new user from Supabase auth
                user = User(
                    supabase_user_id=supabase_user_id,
                    email=email,
                    plan=UserPlan.FREE,
                    role=UserRole.USER,
                    daily_limit=settings.FREE_TIER_DAILY_LIMIT,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                logger.info("user_created_from_supabase", supabase_user_id=supabase_user_id, email=email)

        except AuthException:
            raise
        except Exception as e:
            logger.error("jwt_auth_error", error=str(e))
            raise AuthException(
                message="Authentication failed",
                error_code="AUTH_FAILED",
            )

    # Fallback to API key (backward compatibility)
    elif api_key:
        # Hash the API key for secure lookup
        api_key_hash = hash_api_key(api_key)
        
        result = await db.execute(
            select(User).where(User.api_key_hash == api_key_hash)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Auto-create new user with this API key
            # Store only the hash, not the plain text key
            user = User(
                api_key_hash=api_key_hash,
                plan=UserPlan.FREE,
                role=UserRole.USER,
                daily_limit=settings.FREE_TIER_DAILY_LIMIT,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            # Log only first 4 chars for debugging (not the actual key)
            logger.info("user_created_from_api_key", api_key_prefix=api_key[:4])

    if not user:
        raise AuthException(
            message="Authentication required. Provide Bearer token or API key.",
            error_code="AUTH_REQUIRED",
        )

    # Check if account is active
    if not user.is_active:
        raise AuthException(
            message="Account is inactive",
            error_code="ACCOUNT_INACTIVE",
        )

    # Check if account is banned
    if user.is_banned:
        raise AuthException(
            message="Account is banned",
            error_code="ACCOUNT_BANNED",
        )

    # Reset daily usage if new day
    now = datetime.now(timezone.utc)
    if user.last_reset_date.date() < now.date():
        user.daily_used = 0
        user.last_reset_date = now
        await db.commit()

    # Check rate limit
    if user.daily_used >= user.daily_limit:
        raise RateLimitException(
            message=f"Daily limit exceeded. Your plan: {user.plan}",
            details={
                "limit": user.daily_limit,
                "used": user.daily_used,
                "plan": user.plan,
                "reset_at": (now + timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat(),
            },
        )

    return user


async def get_current_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Verify that the current user has admin role.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def increment_usage(
    user: User,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Increment user's daily usage counter.
    Uses subscription limit first, then falls back to credits.
    """
    from app.models.database import UserCredit, CreditTransaction
    
    # Check if user has reached daily limit
    if user.daily_used >= user.daily_limit:
        # Try to use credits instead
        result = await db.execute(
            select(UserCredit).where(UserCredit.user_id == user.id)
        )
        user_credit = result.scalar_one_or_none()
        
        if user_credit and user_credit.credits > 0:
            # Check if credits are expired
            now = datetime.now(timezone.utc)
            if user_credit.expires_at and user_credit.expires_at < now:
                # Credits expired - reset them
                user_credit.credits = 0
                await db.commit()
                raise RateLimitException(
                    message="Credits have expired. Please purchase a new package.",
                    details={
                        "limit": user.daily_limit,
                        "used": user.daily_used,
                        "credits": 0,
                        "expired": True,
                    },
                )
            
            # Use one credit
            user_credit.credits -= 1
            user_credit.updated_at = now
            
            # Record transaction
            transaction = CreditTransaction(
                user_id=user.id,
                transaction_type="usage",
                credits=-1,
                balance_after=user_credit.credits,
                package_type=None,
                description="Analysis using credit",
            )
            db.add(transaction)
        else:
            # No credits available - raise limit error
            raise RateLimitException(
                message=f"Daily limit exceeded. Your plan: {user.plan}",
                details={
                    "limit": user.daily_limit,
                    "used": user.daily_used,
                    "plan": user.plan,
                    "credits": 0,
                    "reset_at": (now + timedelta(days=1)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    ).isoformat(),
                },
            )

    # Increment daily usage
    user.daily_used = (user.daily_used or 0) + 1
    user.total_analyses = (user.total_analyses or 0) + 1
    await db.commit()


def generate_api_key() -> str:
    """Generate a new API key"""
    return secrets.token_urlsafe(settings.API_KEY_LENGTH)


def generate_api_key_hash(api_key: str) -> str:
    """Generate hash for an API key - utility for migrations"""
    return hash_api_key(api_key)


def generate_jwt_tokens(
    user_id: int,
    email: Optional[str] = None,
    telegram_id: Optional[int] = None,
) -> tuple[str, str]:
    """
    Generate JWT access and refresh tokens for user.

    Args:
        user_id: User ID in database
        email: User email (optional)
        telegram_id: Telegram ID (optional)

    Returns:
        Tuple of (access_token, refresh_token)
    """
    now = datetime.now(timezone.utc)

    # Access token (short-lived)
    access_payload = {
        "sub": str(user_id),
        "email": email,
        "telegram_id": telegram_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    # Refresh token (long-lived)
    refresh_payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return access_token, refresh_token


def verify_jwt_token(
    token: str,
    token_type: str = "access",
) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Token payload

    Raises:
        AuthException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": ["exp", "iat", "sub"],
                "verify_exp": True,
            },
        )

        if payload.get("type") != token_type:
            raise AuthException(
                message=f"Invalid token type. Expected {token_type}",
                error_code="INVALID_TOKEN_TYPE",
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthException(
            message="Token has expired",
            error_code="TOKEN_EXPIRED",
        )
    except jwt.InvalidTokenError as e:
        logger.warning("jwt_verification_failed", error=str(e))
        raise AuthException(
            message="Invalid token",
            error_code="INVALID_TOKEN",
        )


# Alias for backward compatibility
get_api_key = get_current_user
