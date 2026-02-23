"""
Brands management API endpoints.
Allows users to manage custom brands for detection.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.database import CustomBrand, User, BrandCategory
from app.schemas.brand import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    BrandListResponse,
    BrandCategoryResponse,
)
from app.services.audit_logger import AuditLogger, AuditEventType

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.get("/categories", response_model=List[BrandCategoryResponse])
async def get_brand_categories():
    """
    Get all available brand categories.
    
    Returns:
        List of brand categories with labels
    """
    categories = [
        {"value": "bank", "label": "Банки"},
        {"value": "telecom", "label": "Телеком"},
        {"value": "auto", "label": "Авто"},
        {"value": "food", "label": "Еда и рестораны"},
        {"value": "beverage", "label": "Напитки"},
        {"value": "clothing", "label": "Одежда и спорт"},
        {"value": "technology", "label": "Технологии"},
        {"value": "marketplace", "label": "Маркетплейсы"},
        {"value": "bookmaker", "label": "Букмекеры"},
        {"value": "energy", "label": "Энергетика и газ"},
        {"value": "airline", "label": "Авиакомпании"},
        {"value": "retail", "label": "Ритейл"},
        {"value": "pharma", "label": "Фармацевтика"},
        {"value": "cosmetics", "label": "Косметика"},
        {"value": "gaming", "label": "Игры"},
        {"value": "education", "label": "Образование"},
        {"value": "other", "label": "Другое"},
    ]
    return categories


@router.get("", response_model=BrandListResponse)
async def list_brands(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[BrandCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by brand name"),
    active_only: bool = Query(False, description="Show only active brands"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's custom brands.
    
    - **page**: Page number (1-based)
    - **page_size**: Items per page (max 100)
    - **category**: Filter by brand category
    - **search**: Search in brand name and aliases
    - **active_only**: Show only active brands
    """
    offset = (page - 1) * page_size
    
    # Build query
    query = select(CustomBrand).where(
        or_(
            CustomBrand.user_id == current_user.id,
            CustomBrand.user_id.is_(None)  # Include global brands
        )
    )
    
    # Apply filters
    if category:
        query = query.where(CustomBrand.category == category)
    
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            or_(
                CustomBrand.name.ilike(search_filter),
                CustomBrand.description.ilike(search_filter),
            )
        )
    
    if active_only:
        query = query.where(CustomBrand.is_active == True)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.order_by(CustomBrand.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    brands = result.scalars().all()
    
    return BrandListResponse(
        items=[BrandResponse.model_validate(brand) for brand in brands],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific brand by ID.
    """
    query = select(CustomBrand).where(
        CustomBrand.id == brand_id,
        or_(
            CustomBrand.user_id == current_user.id,
            CustomBrand.user_id.is_(None)
        )
    )
    
    result = await db.execute(query)
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    return BrandResponse.model_validate(brand)


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_data: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new custom brand.
    
    - **name**: Brand name (required)
    - **category**: Brand category (default: other)
    - **description**: Optional description
    - **aliases**: List of alternative names
    - **logo_url**: URL to brand logo
    - **detection_threshold**: Detection sensitivity (0.0-1.0)
    """
    # Check for duplicates
    existing_query = select(CustomBrand).where(
        CustomBrand.user_id == current_user.id,
        CustomBrand.name == brand_data.name
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this name already exists"
        )
    
    # Create brand
    brand = CustomBrand(
        user_id=current_user.id,
        **brand_data.model_dump(),
    )
    
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    
    # Log audit event
    audit_logger = AuditLogger(db)
    await audit_logger.log(
        event_type=AuditEventType.DATA_IMPORT,
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        target_type="brand",
        target_id=brand.id,
        changes={"name": brand.name, "category": brand.category.value},
        event_category="brand",
        description=f"Created custom brand: {brand.name}",
    )
    
    return BrandResponse.model_validate(brand)


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing brand.
    
    Only the brand owner can update it.
    """
    # Get brand
    query = select(CustomBrand).where(
        CustomBrand.id == brand_id,
        CustomBrand.user_id == current_user.id
    )
    result = await db.execute(query)
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    # Update fields
    update_data = brand_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    
    await db.commit()
    await db.refresh(brand)

    # Log audit event
    audit_logger = AuditLogger(db)
    await audit_logger.log(
        event_type=AuditEventType.USER_UPDATED,
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        target_type="brand",
        target_id=brand.id,
        changes=update_data,
        event_category="brand",
        description=f"Updated custom brand: {brand.name}",
    )

    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a custom brand.
    
    Only the brand owner can delete it.
    """
    # Get brand
    query = select(CustomBrand).where(
        CustomBrand.id == brand_id,
        CustomBrand.user_id == current_user.id
    )
    result = await db.execute(query)
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    # Delete brand
    await db.delete(brand)
    await db.commit()

    # Log audit event
    audit_logger = AuditLogger(db)
    await audit_logger.log(
        event_type=AuditEventType.DATA_DELETE,
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        target_type="brand",
        target_id=brand_id,
        event_category="brand",
        description=f"Deleted custom brand: {brand.name}",
    )


@router.post("/{brand_id}/toggle", response_model=BrandResponse)
async def toggle_brand_status(
    brand_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Toggle brand active/inactive status.
    """
    # Get brand
    query = select(CustomBrand).where(
        CustomBrand.id == brand_id,
        CustomBrand.user_id == current_user.id
    )
    result = await db.execute(query)
    brand = result.scalar_one_or_none()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    # Toggle status
    brand.is_active = not brand.is_active
    
    await db.commit()
    await db.refresh(brand)

    # Log audit event
    audit_logger = AuditLogger(db)
    await audit_logger.log(
        event_type=AuditEventType.USER_UPDATED,
        actor_user_id=current_user.id,
        actor_email=current_user.email,
        target_type="brand",
        target_id=brand.id,
        changes={"is_active": brand.is_active},
        event_category="brand",
        description=f"Toggled brand status: {brand.name} -> {'active' if brand.is_active else 'inactive'}",
    )

    return BrandResponse.model_validate(brand)
