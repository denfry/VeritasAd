"""add_custom_brands_table

Revision ID: 008
Revises: 007
Create Date: 2026-02-21

Add custom brands table for user-defined brand detection:
- custom_brands: Store user-defined brands for video analysis
- BrandCategory enum for categorizing brands
- Support for aliases, logos, and custom detection thresholds

Features:
- Users can add custom brands to detect in videos
- Brands are categorized (bank, telecom, auto, food, etc.)
- Support for multiple name aliases per brand
- Optional logo storage (base64 or URL)
- Custom detection thresholds per brand
- Global brands (user_id=NULL) for system-wide defaults
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Step 1: Create BrandCategory enum type (PostgreSQL only)
    if dialect == 'postgresql':
        # Check if enum type exists
        result = bind.execute(
            sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'brand_category')")
        ).scalar()
        
        if not result:
            # Create enum type
            brand_category = sa.Enum(
                'bank', 'telecom', 'auto', 'food', 'beverage',
                'clothing', 'technology', 'marketplace', 'bookmaker',
                'energy', 'airline', 'retail', 'pharma', 'cosmetics',
                'gaming', 'education', 'other',
                name='brand_category'
            )
            brand_category.create(bind)

    # Step 2: Create custom_brands table
    op.create_table(
        'custom_brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column(
            'category',
            sa.Enum(
                'bank', 'telecom', 'auto', 'food', 'beverage',
                'clothing', 'technology', 'marketplace', 'bookmaker',
                'energy', 'airline', 'retail', 'pharma', 'cosmetics',
                'gaming', 'education', 'other',
                name='brand_category',
                create_type=dialect == 'postgresql'
            ),
            nullable=False,
            server_default='other'
        ),
        sa.Column('aliases', sa.JSON(), nullable=True),
        sa.Column('logo_base64', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('detection_threshold', sa.Float(), nullable=False, server_default='0.15'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Step 3: Create indexes
    op.create_index('ix_custom_brands_id', 'custom_brands', ['id'], unique=False)
    op.create_index('ix_custom_brands_user_id', 'custom_brands', ['user_id'], unique=False)
    op.create_index('ix_custom_brands_name', 'custom_brands', ['name'], unique=False)
    op.create_index('ix_custom_brands_is_active', 'custom_brands', ['is_active'], unique=False)
    op.create_index('ix_custom_brands_created_at', 'custom_brands', ['created_at'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Drop table
    op.drop_table('custom_brands')

    # Drop enum type (PostgreSQL only)
    if dialect == 'postgresql':
        op.execute("DROP TYPE IF EXISTS brand_category")
