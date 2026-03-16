"""add analyses erids and promo_codes columns

Revision ID: 010
Revises: 009
Create Date: 2026-03-09

Add erids and promo_codes JSON columns to analyses table.
"""
from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "analyses",
        sa.Column("erids", sa.JSON(), nullable=True),
    )
    op.add_column(
        "analyses",
        sa.Column("promo_codes", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analyses", "promo_codes")
    op.drop_column("analyses", "erids")
