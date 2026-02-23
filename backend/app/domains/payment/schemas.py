"""Payment domain schemas."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional


# ==================== SUBSCRIPTION ====================

class PaymentCreateRequest(BaseModel):
    """Payment creation request."""

    plan: Literal["pro", "enterprise"] = Field(..., description="Target plan")
    return_url: Optional[str] = None


class PaymentCreateResponse(BaseModel):
    """Payment creation response."""

    payment_id: str
    status: str
    amount: float
    currency: str
    checkout_url: str


class PaymentWebhookRequest(BaseModel):
    """Payment webhook payload."""

    payment_id: str
    status: Literal["succeeded", "canceled", "failed"]
    metadata: Optional[dict] = None


# ==================== SUBSCRIPTION PLANS ====================

class SubscriptionPlanRequest(BaseModel):
    """Subscription plan selection request."""

    plan: Literal["starter", "pro", "business", "enterprise"] = Field(..., description="Target subscription plan")
    return_url: Optional[str] = None


class SubscriptionPlanResponse(BaseModel):
    """Subscription plan creation response."""

    payment_id: str
    status: str
    amount: float
    currency: str
    checkout_url: str
    plan: str
    daily_limit: int


# ==================== CREDIT PACKAGES ====================

class CreditPackageRequest(BaseModel):
    """Credit package purchase request."""

    package: Literal["micro", "standard", "pro", "business"] = Field(..., description="Credit package type")
    return_url: Optional[str] = None


class CreditPackageResponse(BaseModel):
    """Credit package purchase response."""

    payment_id: str
    status: str
    amount: float
    currency: str
    checkout_url: str
    package_type: str
    credits: int
    validity_days: int
    price_per_analysis: float


# ==================== USER CREDITS ====================

class UserCreditsResponse(BaseModel):
    """User credit balance response."""

    credits: int
    expires_at: Optional[datetime] = None
    total_used: int
    total_purchased: int


class CreditTransactionItem(BaseModel):
    """Credit transaction item."""

    id: int
    transaction_type: str
    credits: int
    balance_after: int
    package_type: Optional[str]
    description: Optional[str]
    created_at: datetime


class CreditHistoryResponse(BaseModel):
    """Credit transaction history response."""

    transactions: list[CreditTransactionItem]
    total: int
