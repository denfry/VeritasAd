"""add_social_source_types

Revision ID: 003
Revises: 002
Create Date: 2026-01-24

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # PostgreSQL - add enum values
    if dialect == 'postgresql':
        op.execute("ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'instagram'")
        op.execute("ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'tiktok'")
        op.execute("ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'vk'")
    # SQLite doesn't support ALTER TYPE - enum values are enforced by application logic


def downgrade() -> None:
    # Enum value removal is not supported in PostgreSQL without type recreation.
    # SQLite doesn't have enum types.
    pass
