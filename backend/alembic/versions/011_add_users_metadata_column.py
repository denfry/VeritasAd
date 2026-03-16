"""add users metadata column

Revision ID: 011
Revises: 010
Create Date: 2026-03-09

Add metadata JSON column to users table.
Model uses mapped_column("metadata", ...) but initial migration created user_metadata.
"""
from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Model expects column name "metadata" (mapped_column("metadata", JSON))
    op.add_column(
        "users",
        sa.Column("metadata", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "metadata")
