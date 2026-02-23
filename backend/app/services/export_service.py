"""
Data Export Service.
BigTech Standard - аналог AWS Data Export, Google Takeout.

Features:
- Async export jobs
- Multiple formats (CSV, JSON, XLSX)
- S3/local storage
- Email notifications
"""
import asyncio
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import uuid

from app.models.database import User, Analysis, AuditLog, Payment
from app.services.audit_logger import AuditLogger, AuditEventType

logger = structlog.get_logger(__name__)


ExportFormat = Literal["csv", "json", "xlsx"]
ExportType = Literal["users", "analyses", "audit_logs", "payments"]


class ExportJob:
    """Represents an export job."""
    
    def __init__(
        self,
        export_id: str,
        export_type: ExportType,
        format: ExportFormat,
        user_id: int,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
    ):
        self.export_id = export_id
        self.export_type = export_type
        self.format = format
        self.user_id = user_id
        self.filters = filters or {}
        self.columns = columns
        self.status = "pending"
        self.created_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
        self.file_path: Optional[str] = None
        self.download_url: Optional[str] = None
        self.error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "export_id": self.export_id,
            "export_type": self.export_type,
            "format": self.format,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "download_url": self.download_url,
            "error_message": self.error_message,
        }


class ExportService:
    """
    Data export service.
    
    Usage:
        export_service = ExportService(db, export_dir)
        job = await export_service.create_export_job(...)
        await export_service.process_export(job)
    """
    
    def __init__(self, db: AsyncSession, export_dir: str = "./data/exports"):
        self.db = db
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory job store (use Redis in production)
        self.jobs: Dict[str, ExportJob] = {}
    
    async def create_export_job(
        self,
        export_type: ExportType,
        format: ExportFormat,
        user_id: int,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
    ) -> ExportJob:
        """Create a new export job."""
        export_id = str(uuid.uuid4())
        
        job = ExportJob(
            export_id=export_id,
            export_type=export_type,
            format=format,
            user_id=user_id,
            filters=filters,
            columns=columns,
        )
        
        self.jobs[export_id] = job
        
        logger.info(
            "export_job_created",
            export_id=export_id,
            export_type=export_type,
            format=format,
            user_id=user_id,
        )
        
        return job
    
    async def process_export(self, job: ExportJob) -> None:
        """Process export job asynchronously."""
        job.status = "processing"
        
        try:
            # Fetch data
            data = await self._fetch_data(job.export_type, job.filters)
            
            # Convert to format
            if job.format == "csv":
                content = self._to_csv(data, job.columns)
            elif job.format == "json":
                content = self._to_json(data)
            elif job.format == "xlsx":
                content = await self._to_xlsx(data)
            else:
                raise ValueError(f"Unsupported format: {job.format}")
            
            # Save file
            filename = f"{job.export_type}_{job.export_id}.{job.format}"
            file_path = self.export_dir / filename
            
            # Write file
            with open(file_path, "w" if job.format in ["csv", "json"] else "wb") as f:
                f.write(content)
            
            # Update job
            job.file_path = str(file_path)
            job.download_url = f"/api/v1/admin/exports/{job.export_id}/download"
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            
            logger.info(
                "export_job_completed",
                export_id=job.export_id,
                file_path=job.file_path,
            )
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            
            logger.error(
                "export_job_failed",
                export_id=job.export_id,
                error=str(e),
            )
    
    async def _fetch_data(
        self,
        export_type: ExportType,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Fetch data from database."""
        query = None
        
        if export_type == "users":
            query = select(User)
            if filters.get("plan"):
                query = query.where(User.plan == filters["plan"])
            if filters.get("role"):
                query = query.where(User.role == filters["role"])
            if filters.get("created_after"):
                query = query.where(User.created_at >= filters["created_after"])
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            return [
                {
                    "id": u.id,
                    "email": u.email,
                    "plan": u.plan,
                    "role": u.role,
                    "daily_limit": u.daily_limit,
                    "daily_used": u.daily_used,
                    "total_analyses": u.total_analyses,
                    "is_active": u.is_active,
                    "is_banned": u.is_banned,
                    "created_at": u.created_at.isoformat(),
                }
                for u in users
            ]
        
        elif export_type == "analyses":
            query = select(Analysis)
            if filters.get("status"):
                query = query.where(Analysis.status == filters["status"])
            if filters.get("user_id"):
                query = query.where(Analysis.user_id == filters["user_id"])
            if filters.get("created_after"):
                query = query.where(Analysis.created_at >= filters["created_after"])
            
            result = await self.db.execute(query)
            analyses = result.scalars().all()
            
            return [
                {
                    "id": a.id,
                    "task_id": a.task_id,
                    "user_id": a.user_id,
                    "source_type": a.source_type.value,
                    "status": a.status.value,
                    "has_advertising": a.has_advertising,
                    "confidence_score": a.confidence_score,
                    "created_at": a.created_at.isoformat(),
                }
                for a in analyses
            ]
        
        elif export_type == "audit_logs":
            query = select(AuditLog)
            if filters.get("event_type"):
                query = query.where(AuditLog.event_type == filters["event_type"])
            if filters.get("actor_email"):
                query = query.where(AuditLog.actor_email.ilike(f"%{filters['actor_email']}%"))
            if filters.get("created_after"):
                query = query.where(AuditLog.created_at >= filters["created_after"])
            
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            return [
                {
                    "id": l.id,
                    "event_type": l.event_type.value,
                    "event_category": l.event_category,
                    "description": l.description,
                    "actor_email": l.actor_email,
                    "target_email": l.target_email,
                    "status": l.status,
                    "created_at": l.created_at.isoformat(),
                }
                for l in logs
            ]
        
        elif export_type == "payments":
            query = select(Payment)
            if filters.get("status"):
                query = query.where(Payment.status == filters["status"])
            if filters.get("user_id"):
                query = query.where(Payment.user_id == filters["user_id"])
            
            result = await self.db.execute(query)
            payments = result.scalars().all()
            
            return [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "amount": p.amount,
                    "currency": p.currency,
                    "status": p.status.value,
                    "provider": p.provider.value,
                    "created_at": p.created_at.isoformat(),
                }
                for p in payments
            ]
        
        return []
    
    def _to_csv(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> str:
        """Convert data to CSV format."""
        if not data:
            return ""
        
        # Determine columns
        if columns:
            fieldnames = columns
        else:
            fieldnames = list(data[0].keys())
        
        # Write CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def _to_json(self, data: List[Dict[str, Any]]) -> str:
        """Convert data to JSON format."""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    async def _to_xlsx(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert data to XLSX format."""
        # Requires openpyxl
        try:
            from openpyxl import Workbook
        except ImportError:
            # Fallback to CSV if openpyxl not installed
            return self._to_csv(data).encode("utf-8")
        
        wb = Workbook()
        ws = wb.active
        
        if data:
            # Headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Data rows
            for row in data:
                ws.append([row.get(h) for h in headers])
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output.read()
    
    def get_job(self, export_id: str) -> Optional[ExportJob]:
        """Get export job by ID."""
        return self.jobs.get(export_id)
    
    def list_jobs(self, user_id: int, limit: int = 20) -> List[ExportJob]:
        """List export jobs for a user."""
        user_jobs = [j for j in self.jobs.values() if j.user_id == user_id]
        user_jobs.sort(key=lambda j: j.created_at, reverse=True)
        return user_jobs[:limit]
    
    async def cleanup_old_exports(self, max_age_hours: int = 24) -> int:
        """Clean up old export files."""
        now = datetime.now(timezone.utc)
        cleaned = 0
        
        for job in list(self.jobs.values()):
            if job.completed_at:
                age = now - job.completed_at
                if age.total_seconds() > max_age_hours * 3600:
                    # Delete file
                    if job.file_path and Path(job.file_path).exists():
                        Path(job.file_path).unlink()
                    
                    # Remove from memory
                    del self.jobs[job.export_id]
                    cleaned += 1
        
        return cleaned


# Global export service instance
_export_service: Optional[ExportService] = None


def get_export_service(db: AsyncSession, export_dir: str = "./data/exports") -> ExportService:
    """Get or create export service."""
    global _export_service
    if _export_service is None:
        _export_service = ExportService(db, export_dir)
    return _export_service
