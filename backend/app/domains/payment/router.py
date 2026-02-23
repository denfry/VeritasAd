"""Payment domain router."""
from datetime import datetime, timezone, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import hmac
import hashlib
import json
import structlog

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.database import (
    get_db, Payment, PaymentStatus, PaymentProvider, User, UserPlan,
    UserCredit, CreditTransaction, CreditPackageType
)

logger = structlog.get_logger(__name__)
router = APIRouter()


# ==================== SUBSCRIPTION PLANS ====================

class SubscriptionPlanRequest(BaseModel):
    plan: Literal["starter", "pro", "business", "enterprise"] = Field(..., description="Target subscription plan")
    return_url: Optional[str] = None


class SubscriptionPlanResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    currency: str
    checkout_url: str
    plan: str
    daily_limit: int


# Plan pricing and limits mapping
PLAN_CONFIGS = {
    "starter": {
        "price": 2900.0,
        "daily_limit": settings.STARTER_TIER_DAILY_LIMIT,
        "description": "For freelancers and light usage",
    },
    "pro": {
        "price": 7900.0,
        "daily_limit": settings.PRO_TIER_DAILY_LIMIT,
        "description": "For small business and marketing teams",
    },
    "business": {
        "price": 19900.0,
        "daily_limit": settings.BUSINESS_TIER_DAILY_LIMIT,
        "description": "For agencies and growing companies",
    },
    "enterprise": {
        "price": 49900.0,
        "daily_limit": settings.ENTERPRISE_TIER_DAILY_LIMIT,
        "description": "For corporations and custom deployments",
    },
}


# ==================== PAY-AS-YOU-GO PACKAGES ====================

class CreditPackageRequest(BaseModel):
    package: Literal["micro", "standard", "pro", "business"] = Field(..., description="Credit package type")
    return_url: Optional[str] = None


class CreditPackageResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    currency: str
    checkout_url: str
    package_type: str
    credits: int
    validity_days: int
    price_per_analysis: float


# Credit package configs
CREDIT_PACKAGE_CONFIGS = {
    "micro": {
        "credits": settings.PAYG_MICRO_CREDITS,
        "price": settings.PAYG_MICRO_PRICE,
        "validity_days": settings.PAYG_MICRO_VALIDITY_DAYS,
    },
    "standard": {
        "credits": settings.PAYG_STANDARD_CREDITS,
        "price": settings.PAYG_STANDARD_PRICE,
        "validity_days": settings.PAYG_STANDARD_VALIDITY_DAYS,
    },
    "pro": {
        "credits": settings.PAYG_PRO_CREDITS,
        "price": settings.PAYG_PRO_PRICE,
        "validity_days": settings.PAYG_PRO_VALIDITY_DAYS,
    },
    "business": {
        "credits": settings.PAYG_BUSINESS_CREDITS,
        "price": settings.PAYG_BUSINESS_PRICE,
        "validity_days": settings.PAYG_BUSINESS_VALIDITY_DAYS,
    },
}


# ==================== USER CREDITS ====================

class UserCreditsResponse(BaseModel):
    credits: int
    expires_at: Optional[datetime] = None
    total_used: int
    total_purchased: int


class CreditTransactionItem(BaseModel):
    id: int
    transaction_type: str
    credits: int
    balance_after: int
    package_type: Optional[str]
    description: Optional[str]
    created_at: datetime


class CreditHistoryResponse(BaseModel):
    transactions: list[CreditTransactionItem]
    total: int


def verify_yookassa_signature(request: Request, body: bytes) -> bool:
    """
    Verify YooKassa webhook HMAC-SHA256 signature.
    """
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        return False

    if not settings.YOOKASSA_SECRET_KEY:
        logger.warning("yookassa_secret_not_configured")
        return False

    try:
        signature_value = signature.replace("sha256=", "")
        expected = hmac.new(
            settings.YOOKASSA_SECRET_KEY.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature_value, expected)
    except Exception:
        return False


# ==================== SUBSCRIPTION ENDPOINTS ====================

@router.post("/subscription/create", response_model=SubscriptionPlanResponse)
async def create_subscription(
    payload: SubscriptionPlanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a subscription payment for plan upgrade."""

    if payload.plan not in PLAN_CONFIGS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    config = PLAN_CONFIGS[payload.plan]
    amount = config["price"]
    payment_id = uuid.uuid4().hex
    checkout_url = f"{settings.YOOKASSA_RETURN_URL}?payment_id={payment_id}"

    payment = Payment(
        user_id=user.id,
        amount=amount,
        currency="RUB",
        status=PaymentStatus.PENDING,
        provider=PaymentProvider.YOOKASSA,
        provider_payment_id=payment_id,
        payment_metadata={
            "type": "subscription",
            "plan": payload.plan,
            "return_url": payload.return_url or settings.YOOKASSA_RETURN_URL,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    db.add(payment)
    await db.commit()

    return SubscriptionPlanResponse(
        payment_id=payment_id,
        status=payment.status,
        amount=amount,
        currency="RUB",
        checkout_url=checkout_url,
        plan=payload.plan,
        daily_limit=config["daily_limit"],
    )


# ==================== PAY-AS-YOU-GO ENDPOINTS ====================

@router.post("/credits/package", response_model=CreditPackageResponse)
async def purchase_credit_package(
    payload: CreditPackageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Purchase a pay-as-you-go credit package."""

    if payload.package not in CREDIT_PACKAGE_CONFIGS:
        raise HTTPException(status_code=400, detail="Invalid package type")

    config = CREDIT_PACKAGE_CONFIGS[payload.package]
    amount = config["price"]
    payment_id = uuid.uuid4().hex
    checkout_url = f"{settings.YOOKASSA_RETURN_URL}?payment_id={payment_id}"

    payment = Payment(
        user_id=user.id,
        amount=amount,
        currency="RUB",
        status=PaymentStatus.PENDING,
        provider=PaymentProvider.YOOKASSA,
        provider_payment_id=payment_id,
        payment_metadata={
            "type": "credits",
            "package": payload.package,
            "credits": config["credits"],
            "validity_days": config["validity_days"],
            "return_url": payload.return_url or settings.YOOKASSA_RETURN_URL,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    db.add(payment)
    await db.commit()

    price_per_analysis = amount / config["credits"]

    return CreditPackageResponse(
        payment_id=payment_id,
        status=payment.status,
        amount=amount,
        currency="RUB",
        checkout_url=checkout_url,
        package_type=payload.package,
        credits=config["credits"],
        validity_days=config["validity_days"],
        price_per_analysis=round(price_per_analysis, 2),
    )


# ==================== USER CREDITS ENDPOINTS ====================

@router.get("/credits", response_model=UserCreditsResponse)
async def get_user_credits(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's credit balance."""

    result = await db.execute(
        select(UserCredit).where(UserCredit.user_id == user.id)
    )
    user_credit = result.scalar_one_or_none()

    if not user_credit:
        return UserCreditsResponse(
            credits=0,
            expires_at=None,
            total_used=0,
            total_purchased=0,
        )

    # Calculate total purchased and used from transactions
    transactions_result = await db.execute(
        select(CreditTransaction).where(
            CreditTransaction.user_id == user.id
        ).order_by(CreditTransaction.created_at.desc())
    )
    transactions = transactions_result.scalars().all()

    total_purchased = sum(t.credits for t in transactions if t.credits > 0)
    total_used = abs(sum(t.credits for t in transactions if t.credits < 0))

    return UserCreditsResponse(
        credits=user_credit.credits,
        expires_at=user_credit.expires_at,
        total_used=total_used,
        total_purchased=total_purchased,
    )


@router.get("/credits/history", response_model=CreditHistoryResponse)
async def get_credit_history(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's credit transaction history."""

    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user.id)
        .order_by(CreditTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    transactions = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user.id)
    )
    total = len(count_result.scalars().all())

    return CreditHistoryResponse(
        transactions=[
            CreditTransactionItem(
                id=t.id,
                transaction_type=t.transaction_type,
                credits=t.credits,
                balance_after=t.balance_after,
                package_type=t.package_type,
                description=t.description,
                created_at=t.created_at,
            )
            for t in transactions
        ],
        total=total,
    )


# ==================== WEBHOOK ENDPOINT ====================

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle YooKassa payment webhooks with signature verification.
    Processes both subscription and credit package payments.
    """
    body = await request.body()

    if not verify_yookassa_signature(request, body):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(
            "webhook_signature_invalid",
            client_ip=client_ip,
            headers=dict(request.headers),
        )
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload_data = json.loads(body)
        payment_id = payload_data.get("payment_id") or payload_data.get("id")
        status_raw = payload_data.get("status", "canceled")

        # Map YooKassa status to our status
        status_map = {
            "succeeded": PaymentStatus.SUCCEEDED,
            "waiting_for_payment": PaymentStatus.PENDING,
            "canceled": PaymentStatus.CANCELED,
            "failed": PaymentStatus.FAILED,
        }
        status = status_map.get(status_raw, PaymentStatus.CANCELED)

    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(400, f"Invalid payload: {str(e)}")

    result = await db.execute(
        select(Payment).where(Payment.provider_payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        logger.warning("payment_not_found", payment_id=payment_id)
        raise HTTPException(404, "Payment not found")

    payment.status = status
    if payment.payment_metadata is None:
        payment.payment_metadata = {}
    payment.payment_metadata["webhook_received_at"] = datetime.now(timezone.utc).isoformat()
    payment.payment_metadata["yookassa_status"] = status_raw

    await db.commit()

    if status == PaymentStatus.SUCCEEDED and payment.status != PaymentStatus.SUCCEEDED:
        # Payment just succeeded - process it
        metadata = payment.payment_metadata or {}
        payment_type = metadata.get("type", "subscription")

        try:
            if payment_type == "subscription":
                # Process subscription upgrade
                plan = metadata.get("plan", "pro")
                result_user = await db.execute(
                    select(User).where(User.id == payment.user_id)
                )
                user = result_user.scalar_one_or_none()

                if user:
                    # Map plan string to UserPlan enum
                    plan_map = {
                        "starter": UserPlan.STARTER,
                        "pro": UserPlan.PRO,
                        "business": UserPlan.BUSINESS,
                        "enterprise": UserPlan.ENTERPRISE,
                    }
                    user_plan = plan_map.get(plan, UserPlan.PRO)
                    user.plan = user_plan

                    # Set daily limit based on plan
                    limit_map = {
                        "starter": settings.STARTER_TIER_DAILY_LIMIT,
                        "pro": settings.PRO_TIER_DAILY_LIMIT,
                        "business": settings.BUSINESS_TIER_DAILY_LIMIT,
                        "enterprise": settings.ENTERPRISE_TIER_DAILY_LIMIT,
                    }
                    user.daily_limit = limit_map.get(plan, settings.PRO_TIER_DAILY_LIMIT)

                    logger.info(
                        "user_plan_upgraded",
                        user_id=user.id,
                        plan=plan,
                        payment_id=payment_id,
                    )
                    await db.commit()

            elif payment_type == "credits":
                # Process credit package purchase
                package_type = metadata.get("package", "standard")
                credits = metadata.get("credits", 0)
                validity_days = metadata.get("validity_days", 30)

                if package_type not in CREDIT_PACKAGE_CONFIGS:
                    logger.error("invalid_credit_package", package_type=package_type)
                    return {"status": "ok"}

                result_user = await db.execute(
                    select(User).where(User.id == payment.user_id)
                )
                user = result_user.scalar_one_or_none()

                if user:
                    # Get or create user credit balance
                    credit_result = await db.execute(
                        select(UserCredit).where(UserCredit.user_id == user.id)
                    )
                    user_credit = credit_result.scalar_one_or_none()

                    if not user_credit:
                        user_credit = UserCredit(
                            user_id=user.id,
                            credits=0,
                        )
                        db.add(user_credit)

                    # Add credits and set expiration
                    user_credit.credits += credits
                    user_credit.expires_at = datetime.now(timezone.utc) + timedelta(days=validity_days)

                    # Create transaction record
                    transaction = CreditTransaction(
                        user_id=user.id,
                        transaction_type="purchase",
                        credits=credits,
                        balance_after=user_credit.credits,
                        package_type=package_type,
                        payment_id=payment.id,
                        description=f"Purchased {package_type} package: {credits} credits",
                    )
                    db.add(transaction)

                    logger.info(
                        "credits_purchased",
                        user_id=user.id,
                        package_type=package_type,
                        credits=credits,
                        payment_id=payment_id,
                    )
                    await db.commit()

        except Exception as e:
            logger.error(
                "payment_processing_error",
                payment_id=payment_id,
                error=str(e),
            )
            # Don't rollback - payment status should be saved
            # but log the error for investigation

    return {"status": "ok"}
