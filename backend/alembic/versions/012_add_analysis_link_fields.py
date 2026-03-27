"""add analysis link and CTA fields

Revision ID: 012
Revises: 011
Create Date: 2026-03-21

Add link_score, cta_matches, and commercial_urls columns to analyses.
"""
from alembic import op
import sqlalchemy as sa


revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analyses", sa.Column("link_score", sa.Float(), nullable=True))
    op.add_column("analyses", sa.Column("cta_matches", sa.JSON(), nullable=True))
    op.add_column("analyses", sa.Column("commercial_urls", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("analyses", "commercial_urls")
    op.drop_column("analyses", "cta_matches")
    op.drop_column("analyses", "link_score")
