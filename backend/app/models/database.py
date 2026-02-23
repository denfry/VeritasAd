from datetime import datetime, timezone
from typing import AsyncGenerator, Optional, List, Dict
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Index, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy.pool import NullPool, QueuePool
import enum
from app.core.config import settings

Base = declarative_base()

class UserPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SourceType(str, enum.Enum):
    FILE = "file"
    URL = "url"
    YOUTUBE = "youtube"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    VK = "vk"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"

class PaymentProvider(str, enum.Enum):
    YOOKASSA = "yookassa"


class BrandCategory(str, enum.Enum):
    """Brand categories for organization."""
    BANK = "bank"
    TELECOM = "telecom"
    AUTO = "auto"
    FOOD = "food"
    BEVERAGE = "beverage"
    CLOTHING = "clothing"
    TECHNOLOGY = "technology"
    MARKETPLACE = "marketplace"
    BOOKMAKER = "bookmaker"
    ENERGY = "energy"
    AIRLINE = "airline"
    RETAIL = "retail"
    PHARMA = "pharma"
    COSMETICS = "cosmetics"
    GAMING = "gaming"
    EDUCATION = "education"
    OTHER = "other"


class AuditEventType(str, enum.Enum):
    """Audit log event types - BigTech standard."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET = "password_reset"
    TWO_FA_ENABLED = "two_fa_enabled"
    TWO_FA_DISABLED = "two_fa_disabled"
    
    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_BANNED = "user.banned"
    USER_UNBANNED = "user.unbanned"
    USER_ACTIVATED = "user.activated"
    USER_DEACTIVATED = "user.deactivated"
    ROLE_CHANGED = "role.changed"
    PLAN_CHANGED = "plan.changed"
    
    # Admin actions
    ADMIN_LOGIN = "admin.login"
    ADMIN_LOGOUT = "admin.logout"
    ADMIN_USER_VIEW = "admin.user.view"
    ADMIN_USER_LIST = "admin.user.list"
    ADMIN_USER_UPDATE = "admin.user.update"
    ADMIN_ANALYTICS_VIEW = "admin.analytics.view"
    ADMIN_EXPORT = "admin.export"
    ADMIN_IMPERSONATE = "admin.impersonate"
    
    # Data operations
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    DATA_DELETE = "data.delete"
    
    # Security
    SESSION_REVOKED = "session.revoked"
    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"
    IP_WHITELIST_ADDED = "ip.whitelist.added"
    IP_WHITELIST_REMOVED = "ip.whitelist.removed"
    
    # System
    SETTINGS_CHANGED = "settings.changed"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_REVOKED = "permission.revoked"


class AuditLog(Base):
    """
    Audit log model for tracking all admin actions and security events.
    BigTech standard - similar to AWS CloudTrail, Google Cloud Audit Logs.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Event info
    event_type: Mapped[str] = mapped_column(SQLEnum(AuditEventType, name="audit_event_type"), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # auth, user, admin, security, system
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Actor (who performed the action)
    actor_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    actor_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 max length
    actor_user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Target (what was acted upon)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # user, analysis, payment, etc.
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Changes (for update events)
    changes: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    event_metadata: Mapped[Optional[Dict]] = mapped_column("metadata", JSON, nullable=True)
    
    # Result
    status: Mapped[str] = mapped_column(String(20), default="success", index=True)  # success, failure, denied
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_audit_logs_actor_created", "actor_user_id", "created_at"),
        Index("idx_audit_logs_event_type_created", "event_type", "created_at"),
        Index("idx_audit_logs_target", "target_type", "target_id"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # API key hash for lookup (SHA-256 hex)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True, nullable=True)
    # Encrypted API key (if retrieval is needed) - optional
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    supabase_user_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Telegram integration
    telegram_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True, index=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    telegram_link_token: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    telegram_linked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    plan: Mapped[str] = mapped_column(SQLEnum(UserPlan, name="user_plan"), default=UserPlan.FREE, nullable=False)
    role: Mapped[str] = mapped_column(SQLEnum(UserRole, name="user_role"), default=UserRole.USER, nullable=False)
    daily_limit: Mapped[int] = mapped_column(Integer, default=100, server_default='100', nullable=False)
    daily_used: Mapped[int] = mapped_column(Integer, default=0, server_default='0', nullable=False)
    last_reset_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    total_analyses: Mapped[int] = mapped_column(Integer, default=0, server_default='0', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true', nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_metadata: Mapped[Optional[Dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    video_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str] = mapped_column(SQLEnum(SourceType, name="source_type"), nullable=False)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    has_advertising: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    visual_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    audio_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    text_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    disclosure_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    detected_brands: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    detected_keywords: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disclosure_markers: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    erids: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    promo_codes: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    ad_classification: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    ad_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(SQLEnum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="RUB", nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(PaymentStatus, name="payment_status"), default=PaymentStatus.PENDING, nullable=False)
    provider: Mapped[str] = mapped_column(SQLEnum(PaymentProvider, name="payment_provider"), default=PaymentProvider.YOOKASSA, nullable=False)
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_metadata: Mapped[Optional[Dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class CreditPackageType(str, enum.Enum):
    """Pay-as-you-go credit package types."""
    MICRO = "micro"          # 100 credits
    STANDARD = "standard"    # 500 credits
    PRO = "pro"              # 1,500 credits
    BUSINESS = "business"    # 8,000 credits


class UserCredit(Base):
    """
    User credit balance for pay-as-you-go analyses.
    Credits are consumed when analysis is performed.
    """
    __tablename__ = "user_credits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to user
    user: Mapped["User"] = relationship("User", back_populates="credits")


class CreditTransaction(Base):
    """
    Transaction log for credit purchases and usage.
    """
    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # purchase, usage, refund, expired
    credits: Mapped[int] = mapped_column(Integer, nullable=False)  # positive for add, negative for use
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    package_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # micro, standard, pro, business
    payment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payments.id"), nullable=True)
    analysis_id: Mapped[Optional[int]] = mapped_column(ForeignKey("analyses.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="credit_transactions")
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="credit_transactions")
    analysis: Mapped[Optional["Analysis"]] = relationship("Analysis", back_populates="credit_transactions")


# Add back-references to User model
User.credits = relationship("UserCredit", back_populates="user", uselist=False, cascade="all, delete-orphan")
User.credit_transactions = relationship("CreditTransaction", back_populates="user", cascade="all, delete-orphan")
Payment.credit_transactions = relationship("CreditTransaction", back_populates="payment", cascade="all, delete-orphan")
Analysis.credit_transactions = relationship("CreditTransaction", back_populates="analysis", cascade="all, delete-orphan")


class CustomBrand(Base):
    """
    Custom brand model for user-defined brand detection.
    Allows users to add their own brands for detection in videos.
    """
    __tablename__ = "custom_brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    
    # Brand info
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(SQLEnum(BrandCategory, name="brand_category"), default=BrandCategory.OTHER, nullable=False)
    
    # Aliases and variations (JSON array of strings)
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Logo for visual matching (optional - stored as base64 or path)
    logo_base64: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Detection settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    detection_threshold: Mapped[float] = mapped_column(Float, default=0.15, nullable=False)
    
    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand_metadata: Mapped[Optional[Dict]] = mapped_column("metadata", JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to user
    user: Mapped[Optional["User"]] = relationship("User", back_populates="custom_brands")


# Add back-reference to User model
User.custom_brands = relationship("CustomBrand", back_populates="user", cascade="all, delete-orphan")

# Configure engine based on database type
if "postgresql" in settings.DATABASE_URL:
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
else:
    # SQLite doesn't support pool_size, max_overflow, pool_timeout, pool_recycle
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=NullPool,
    )

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db() -> None:
    await engine.dispose()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
