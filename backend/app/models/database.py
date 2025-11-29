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
    PRO = "pro"
    ENTERPRISE = "enterprise"

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

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    telegram_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True)
    plan: Mapped[str] = mapped_column(SQLEnum(UserPlan, name="user_plan"), default=UserPlan.FREE, nullable=False)
    daily_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    daily_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reset_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    total_analyses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
    status: Mapped[str] = mapped_column(SQLEnum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

# Configure engine based on database type
if "postgresql" in settings.DATABASE_URL:
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=QueuePool,
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
