"""Password hashing helpers for native JWT authentication (thesis sec. 3.4).

Uses the ``bcrypt`` library directly (rather than passlib) to avoid the known
passlib 1.7.4 / bcrypt 4.x+ backend-detection incompatibility, and to handle
bcrypt's 72-byte input limit explicitly. JWT creation/verification lives in
``app.core.dependencies`` and is reused by the ``/auth`` router.
"""
from __future__ import annotations

import bcrypt

# bcrypt only considers the first 72 bytes of the password.
_BCRYPT_MAX_BYTES = 72


def _prepare(password: str) -> bytes:
    raw = (password or "").encode("utf-8")
    return raw[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    """Return a bcrypt hash for a plaintext password."""
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(_prepare(password), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
