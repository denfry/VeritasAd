"""create jobs table

Revision ID: 20241229_0001
Revises:
Create Date: 2025-12-05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20241229_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("input_url", sa.Text(), nullable=True),
        sa.Column("input_type", sa.String(length=32), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("status", sa.Enum("pending", "processing", "completed", "failed", name="jobstatus"), nullable=False),
        sa.Column("result_path", sa.Text(), nullable=True),
        sa.Column("result_url", sa.Text(), nullable=True),
        sa.Column("media_path", sa.Text(), nullable=True),
        sa.Column("media_url", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("jobs")

