"""add_ad_classification_fields

Revision ID: 002
Revises: 001
Create Date: 2026-01-24

Note: This migration is a no-op because the columns were already added in migration 001.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: columns ad_classification and ad_reason were already added in migration 001
    pass


def downgrade() -> None:
    # No-op: columns will be dropped in migration 001 downgrade
    pass
