"""add claims column to analyses for verifiable claim extraction

Revision ID: 015
Revises: 014
Create Date: 2026-06-17

Adds analyses.claims (JSONB on PostgreSQL, JSON on SQLite) to store the extracted
verifiable advertising claims (VeritasAd 2.0, M2 — roadmap §7). Nullable and
additive, so existing analyses and behaviour are unaffected.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # JSONB on PostgreSQL, generic JSON elsewhere (mirrors JSONB_VARIANT in the model).
    claims_type = sa.JSON().with_variant(JSONB, "postgresql")
    op.add_column("analyses", sa.Column("claims", claims_type, nullable=True))


def downgrade() -> None:
    op.drop_column("analyses", "claims")
