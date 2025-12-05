import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, String, Text

from .database import Base


class JobStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    input_url = Column(Text, nullable=True)
    input_type = Column(String(32), nullable=False)
    platform = Column(String(32), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    result_path = Column(Text, nullable=True)
    result_url = Column(Text, nullable=True)
    media_path = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

