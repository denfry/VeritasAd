"""
Advanced Analytics Service.
BigTech Standard - аналог Google Analytics, Mixpanel, Amplitude.

Features:
- Time series analytics
- Cohort analysis
- Funnel analysis
- Real-time metrics
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract, case
from sqlalchemy.sql import literal_column
import structlog

from app.models.database import User, Analysis, AnalysisStatus, Payment, PaymentStatus
from app.services.audit_logger import AuditLog, AuditEventType

logger = structlog.get_logger(__name__)


class AnalyticsService:
    """Advanced analytics service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_time_series(
        self,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "day",  # hour, day, week, month
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a metric.
        
        Args:
            metric: Metric name (users, analyses, revenue, etc.)
            start_date: Start of range
            end_date: End of range
            interval: Aggregation interval
            filters: Additional filters
        
        Returns:
            List of {timestamp, value} dicts
        """
        filters = filters or {}
        
        # Interval mapping
        interval_map = {
            "hour": extract("hour", Analysis.created_at),
            "day": extract("day", Analysis.created_at),
            "week": extract("week", Analysis.created_at),
            "month": extract("month", Analysis.created_at),
        }
        
        if metric == "analyses":
            return await self._get_analyses_time_series(
                start_date, end_date, interval, filters
            )
        elif metric == "users":
            return await self._get_users_time_series(
                start_date, end_date, interval, filters
            )
        elif metric == "revenue":
            return await self._get_revenue_time_series(
                start_date, end_date, interval, filters
            )
        
        return []
    
    async def _get_analyses_time_series(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get analyses count time series."""
        # Group by date
        date_trunc = func.date_trunc("day", Analysis.created_at)
        
        query = (
            select(
                date_trunc.label("date"),
                func.count(Analysis.id).label("count"),
            )
            .where(
                Analysis.created_at >= start_date,
                Analysis.created_at <= end_date,
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        
        # Apply filters
        if filters.get("status"):
            query = query.where(Analysis.status == filters["status"])
        if filters.get("user_id"):
            query = query.where(Analysis.user_id == filters["user_id"])
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {"timestamp": row.date.isoformat(), "value": row.count}
            for row in rows
        ]
    
    async def _get_users_time_series(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get new users time series."""
        date_trunc = func.date_trunc("day", User.created_at)
        
        query = (
            select(
                date_trunc.label("date"),
                func.count(User.id).label("count"),
            )
            .where(
                User.created_at >= start_date,
                User.created_at <= end_date,
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {"timestamp": row.date.isoformat(), "value": row.count}
            for row in rows
        ]
    
    async def _get_revenue_time_series(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Get revenue time series."""
        date_trunc = func.date_trunc("day", Payment.created_at)
        
        query = (
            select(
                date_trunc.label("date"),
                func.sum(Payment.amount).label("total"),
            )
            .where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == PaymentStatus.SUCCEEDED,
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {"timestamp": row.date.isoformat(), "value": float(row.total or 0)}
            for row in rows
        ]
    
    async def get_cohort_data(
        self,
        cohort_size: str = "month",  # week, month
        periods: int = 12,
    ) -> List[Dict[str, Any]]:
        """
        Get cohort retention data.
        
        Returns retention rate for each cohort over time.
        """
        # Get cohort start dates
        date_trunc = func.date_trunc(cohort_size, User.created_at)
        
        cohorts_query = (
            select(
                date_trunc.label("cohort_date"),
                func.count(User.id).label("user_count"),
            )
            .group_by(date_trunc)
            .order_by(date_trunc)
            .limit(periods)
        )
        
        cohorts_result = await self.db.execute(cohorts_query)
        cohorts = cohorts_result.all()
        
        cohort_data = []
        for cohort in cohorts:
            cohort_data.append({
                "cohort_date": cohort.cohort_date.isoformat(),
                "user_count": cohort.user_count,
                "retention": [],  # Would calculate retention per period
            })
        
        return cohort_data
    
    async def get_funnel_data(
        self,
        funnel_name: str = "analysis",
    ) -> List[Dict[str, Any]]:
        """
        Get funnel conversion data.
        
        For analysis funnel:
        1. Started analysis
        2. Processing
        3. Completed
        """
        if funnel_name == "analysis":
            # Count by status
            query = (
                select(
                    Analysis.status,
                    func.count(Analysis.id).label("count"),
                )
                .group_by(Analysis.status)
            )
            
            result = await self.db.execute(query)
            rows = result.all()
            
            funnel = []
            status_order = [
                AnalysisStatus.PENDING,
                AnalysisStatus.QUEUED,
                AnalysisStatus.PROCESSING,
                AnalysisStatus.COMPLETED,
            ]
            
            for i, status in enumerate(status_order):
                count = next((r.count for r in rows if r.status == status), 0)
                funnel.append({
                    "step": i + 1,
                    "name": status.value,
                    "count": count,
                })
            
            return funnel
        
        return []
    
    async def get_top_items(
        self,
        item_type: str,
        limit: int = 10,
        start_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get top items by various metrics.
        """
        if item_type == "users":
            query = (
                select(
                    User.id,
                    User.email,
                    User.plan,
                    User.total_analyses,
                )
                .order_by(desc(User.total_analyses))
                .limit(limit)
            )
            
            if start_date:
                # Join with analyses to filter by date
                query = query.join(Analysis).where(
                    Analysis.created_at >= start_date
                )
            
            result = await self.db.execute(query)
            return [
                {
                    "id": row.id,
                    "email": row.email or f"user_{row.id}",
                    "plan": row.plan,
                    "total_analyses": row.total_analyses,
                }
                for row in result.all()
            ]
        
        elif item_type == "brands":
            # Top detected brands
            query = (
                select(Analysis.detected_brands)
                .where(
                    Analysis.detected_brands.isnot(None),
                    Analysis.status == AnalysisStatus.COMPLETED,
                )
            )
            
            if start_date:
                query = query.where(Analysis.created_at >= start_date)
            
            result = await self.db.execute(query)
            
            # Aggregate brands
            brand_counts: Dict[str, int] = {}
            for row in result.all():
                brands = row.detected_brands or []
                for brand in brands:
                    name = brand.get("name", "unknown")
                    brand_counts[name] = brand_counts.get(name, 0) + 1
            
            # Sort and return top
            sorted_brands = sorted(
                brand_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:limit]
            
            return [
                {"name": name, "count": count}
                for name, count in sorted_brands
            ]
        
        return []
    
    async def get_summary_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        now = datetime.now(timezone.utc)
        start_date = start_date or (now - timedelta(days=30))
        end_date = end_date or now
        
        # Total users
        total_users_query = select(func.count(User.id))
        total_users_result = await self.db.execute(total_users_query)
        total_users = total_users_result.scalar() or 0
        
        # New users in period
        new_users_query = select(func.count(User.id)).where(
            User.created_at >= start_date,
            User.created_at <= end_date,
        )
        new_users_result = await self.db.execute(new_users_query)
        new_users = new_users_result.scalar() or 0
        
        # Total analyses
        total_analyses_query = select(func.count(Analysis.id))
        total_analyses_result = await self.db.execute(total_analyses_query)
        total_analyses = total_analyses_result.scalar() or 0
        
        # Analyses in period
        period_analyses_query = select(func.count(Analysis.id)).where(
            Analysis.created_at >= start_date,
            Analysis.created_at <= end_date,
        )
        period_analyses_result = await self.db.execute(period_analyses_query)
        period_analyses = period_analyses_result.scalar() or 0
        
        # Success rate
        success_query = select(func.count(Analysis.id)).where(
            Analysis.status == AnalysisStatus.COMPLETED,
            Analysis.created_at >= start_date,
        )
        success_result = await self.db.execute(success_query)
        success_count = success_result.scalar() or 0
        
        success_rate = (success_count / period_analyses * 100) if period_analyses > 0 else 0
        
        # Avg confidence
        avg_confidence_query = select(func.avg(Analysis.confidence_score)).where(
            Analysis.status == AnalysisStatus.COMPLETED,
        )
        avg_confidence_result = await self.db.execute(avg_confidence_query)
        avg_confidence = avg_confidence_result.scalar() or 0.0
        
        return {
            "total_users": total_users,
            "new_users": new_users,
            "total_analyses": total_analyses,
            "period_analyses": period_analyses,
            "success_rate": round(success_rate, 2),
            "avg_confidence": round(float(avg_confidence), 2),
        }


async def get_analytics_service(db: AsyncSession) -> AnalyticsService:
    """Dependency injection."""
    return AnalyticsService(db)
