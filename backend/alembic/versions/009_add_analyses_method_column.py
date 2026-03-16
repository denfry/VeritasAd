"""add analyses method column

Revision ID: 009
Revises: 008
Create Date: 2026-03-09

Add method column to analyses table (e.g. upload vs url).
"""
from alembic import op
import sqlalchemy as sa


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "analyses",
        sa.Column("method", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analyses", "method")
