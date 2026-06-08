"""add hashed_password to users for native JWT auth

Revision ID: 014
Revises: 013
Create Date: 2026-06-07

Adds users.hashed_password (bcrypt) to support the native /auth register/login
flow described in the thesis (sec. 3.4). Nullable so existing Supabase / API-key
users are unaffected.
"""
from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
