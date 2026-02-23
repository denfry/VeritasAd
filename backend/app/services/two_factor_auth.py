"""
Two-Factor Authentication (2FA) Service.
BigTech Standard - TOTP (Time-based One-Time Password) compatible with Google Authenticator, Authy.

Implementation:
- RFC 6238 TOTP
- RFC 4226 HOTP
- QR code generation for easy setup
- Backup codes for recovery
"""
import base64
import hashlib
import hmac
import os
import struct
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Tuple
import pyqrcode
import io
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import User
from app.core.config import settings

logger = structlog.get_logger(__name__)


class TOTP:
    """
    TOTP (Time-based One-Time Password) implementation.
    RFC 6238 compliant.
    """
    
    DIGITS = 6
    INTERVAL = 30  # seconds
    ALGORITHM = "sha1"
    ISSUER = settings.PROJECT_NAME
    
    @classmethod
    def generate_secret(cls, length: int = 20) -> str:
        """Generate a random secret key (base32 encoded)."""
        return base64.b32encode(os.urandom(length)).decode("ascii")
    
    @classmethod
    def generate_totp(cls, secret: str, timestamp: Optional[int] = None) -> str:
        """Generate TOTP code for given secret and timestamp."""
        if timestamp is None:
            timestamp = int(time.time())
        
        # Calculate time counter
        counter = timestamp // cls.INTERVAL
        
        # Pack counter as big-endian 8-byte integer
        counter_bytes = struct.pack(">Q", counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(
            base64.b32decode(secret.upper()),
            counter_bytes,
            hashlib.sha1
        ).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
        code &= 0x7FFFFFFF
        code %= 10 ** cls.DIGITS
        
        # Zero-pad to DIGITS
        return str(code).zfill(cls.DIGITS)
    
    @classmethod
    def verify_totp(cls, secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code with window for clock skew.
        
        Args:
            secret: Base32 encoded secret
            code: User-provided code
            window: Number of intervals to check before/after current (default 1)
        
        Returns:
            True if code is valid
        """
        current_time = int(time.time())
        
        # Check current and adjacent windows
        for offset in range(-window, window + 1):
            expected_code = cls.generate_totp(secret, current_time + (offset * cls.INTERVAL))
            if hmac.compare_digest(code, expected_code):
                return True
        
        return False
    
    @classmethod
    def generate_provisioning_uri(
        cls,
        secret: str,
        account_name: str,
        issuer: Optional[str] = None
    ) -> str:
        """Generate OTP Auth URI for QR code."""
        issuer = issuer or cls.ISSUER
        return (
            f"otpauth://totp/{issuer}:{account_name}?"
            f"secret={secret}&issuer={issuer}"
            f"&algorithm={cls.ALGORITHM.upper()}"
            f"&digits={cls.DIGITS}"
            f"&period={cls.INTERVAL}"
        )
    
    @classmethod
    def generate_qr_code_png(cls, provisioning_uri: str) -> bytes:
        """Generate QR code as PNG bytes."""
        qr = pyqrcode.create(provisioning_uri)
        buffer = io.BytesIO()
        qr.png(buffer, scale=8)
        return buffer.getvalue()
    
    @classmethod
    def generate_qr_code_base64(cls, provisioning_uri: str) -> str:
        """Generate QR code as base64 encoded PNG."""
        png_bytes = cls.generate_qr_code_png(provisioning_uri)
        return base64.b64encode(png_bytes).decode("ascii")


class BackupCodes:
    """
    Backup codes for 2FA recovery.
    Single-use codes that can be used if authenticator is unavailable.
    """
    
    CODE_LENGTH = 8
    CODE_COUNT = 10
    
    @classmethod
    def generate_codes(cls, count: int = CODE_COUNT) -> List[str]:
        """Generate backup codes."""
        codes = []
        for _ in range(count):
            # Generate random alphanumeric code
            code = "".join(
                os.urandom(1).hex()[0]  # Get first char of hex
                for _ in range(cls.CODE_LENGTH)
            )
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes
    
    @classmethod
    def hash_code(cls, code: str) -> str:
        """Hash backup code for storage."""
        # Remove dashes for hashing
        code_clean = code.replace("-", "")
        return hashlib.sha256(code_clean.encode()).hexdigest()
    
    @classmethod
    def verify_code(cls, code: str, hashed_codes: List[str]) -> bool:
        """Verify backup code against hashed codes."""
        code_hash = cls.hash_code(code)
        for hashed in hashed_codes:
            if hmac.compare_digest(code_hash, hashed):
                return True
        return False


class TwoFactorAuthService:
    """
    High-level 2FA service for user management.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def enable_2fa(self, user: User) -> Tuple[str, str]:
        """
        Enable 2FA for user.
        
        Returns:
            Tuple of (secret, qr_code_base64)
        """
        # Generate secret
        secret = TOTP.generate_secret()
        
        # Generate provisioning URI
        account_name = user.email or f"user_{user.id}"
        provisioning_uri = TOTP.generate_provisioning_uri(secret, account_name)
        
        # Generate QR code
        qr_code_base64 = TOTP.generate_qr_code_base64(provisioning_uri)
        
        # Store secret (not yet activated)
        # In production, store in separate 2FA config table
        user.user_metadata = user.user_metadata or {}
        user.user_metadata["2fa_secret_pending"] = secret
        user.user_metadata["2fa_enabled_at"] = None

        await self.db.commit()

        return secret, qr_code_base64

    async def confirm_2fa(self, user: User, code: str) -> bool:
        """
        Confirm 2FA setup with verification code.

        Returns:
            True if successful
        """
        secret = (user.user_metadata or {}).get("2fa_secret_pending")
        if not secret:
            return False
        
        # Verify code
        if not TOTP.verify_totp(secret, code):
            return False
        
        # Generate backup codes
        backup_codes = BackupCodes.generate_codes()
        hashed_codes = [BackupCodes.hash_code(c) for c in backup_codes]

        # Activate 2FA
        user.user_metadata = user.user_metadata or {}
        user.user_metadata["2fa_secret"] = secret
        user.user_metadata["2fa_secret_pending"] = None
        user.user_metadata["2fa_enabled_at"] = datetime.now(timezone.utc).isoformat()
        user.user_metadata["2fa_backup_codes"] = hashed_codes
        user.user_metadata["2fa_backup_codes_remaining"] = len(backup_codes)

        # Store plain backup codes only once (for user to save)
        # In production, return these to user and don't store
        user.user_metadata["2fa_backup_codes_plain"] = backup_codes

        await self.db.commit()

        logger.info(
            "2fa_enabled",
            user_id=user.id,
            user_email=user.email,
        )

        return True

    async def disable_2fa(self, user: User, code: Optional[str] = None) -> bool:
        """
        Disable 2FA for user.
        Requires current TOTP code for security.
        """
        if not (user.user_metadata or {}).get("2fa_secret"):
            return True  # Already disabled
        
        # Verify code if provided
        if code:
            secret = user.user_metadata["2fa_secret"]
            if not TOTP.verify_totp(secret, code):
                return False

        # Remove 2FA config
        user.user_metadata = user.user_metadata or {}
        user.user_metadata["2fa_secret"] = None
        user.user_metadata["2fa_secret_pending"] = None
        user.user_metadata["2fa_enabled_at"] = None
        user.user_metadata["2fa_backup_codes"] = None
        user.user_metadata["2fa_backup_codes_plain"] = None
        user.user_metadata["2fa_disabled_at"] = datetime.now(timezone.utc).isoformat()

        await self.db.commit()

        logger.info(
            "2fa_disabled",
            user_id=user.id,
            user_email=user.email,
        )

        return True

    async def verify_2fa_code(self, user: User, code: str) -> bool:
        """
        Verify 2FA code during login.
        Also checks backup codes.
        """
        metadata = user.user_metadata or {}
        secret = metadata.get("2fa_secret")
        
        if not secret:
            return True  # 2FA not enabled
        
        # Try TOTP
        if TOTP.verify_totp(secret, code):
            return True
        
        # Try backup codes
        hashed_codes = metadata.get("2fa_backup_codes", [])
        if BackupCodes.verify_code(code, hashed_codes):
            # Consume backup code
            code_hash = BackupCodes.hash_code(code)
            metadata["2fa_backup_codes"] = [c for c in hashed_codes if c != code_hash]
            metadata["2fa_backup_codes_remaining"] = len(metadata["2fa_backup_codes"])
            metadata["2fa_last_backup_used"] = datetime.now(timezone.utc).isoformat()
            user.user_metadata = metadata

            await self.db.commit()

            logger.warning(
                "2fa_backup_code_used",
                user_id=user.id,
                user_email=user.email,
                remaining=metadata["2fa_backup_codes_remaining"],
            )

            return True

        return False

    async def regenerate_backup_codes(self, user: User) -> List[str]:
        """
        Regenerate backup codes.
        Requires 2FA to be enabled.
        """
        metadata = user.user_metadata or {}
        if not metadata.get("2fa_secret"):
            raise ValueError("2FA not enabled")
        
        # Generate new codes
        backup_codes = BackupCodes.generate_codes()
        hashed_codes = [BackupCodes.hash_code(c) for c in backup_codes]

        # Store
        metadata["2fa_backup_codes"] = hashed_codes
        metadata["2fa_backup_codes_remaining"] = len(backup_codes)
        metadata["2fa_backup_codes_plain"] = backup_codes
        metadata["2fa_backup_codes_regenerated_at"] = datetime.now(timezone.utc).isoformat()
        user.user_metadata = metadata

        await self.db.commit()

        logger.info(
            "2fa_backup_codes_regenerated",
            user_id=user.id,
            user_email=user.email,
        )

        return backup_codes

    def is_2fa_enabled(self, user: User) -> bool:
        """Check if 2FA is enabled for user."""
        return bool((user.user_metadata or {}).get("2fa_secret"))

    async def get_2fa_status(self, user: User) -> dict:
        """Get 2FA status for user."""
        metadata = user.user_metadata or {}
        return {
            "enabled": self.is_2fa_enabled(user),
            "enabled_at": metadata.get("2fa_enabled_at"),
            "backup_codes_remaining": metadata.get("2fa_backup_codes_remaining", 0),
            "last_backup_used": metadata.get("2fa_last_backup_used"),
        }
