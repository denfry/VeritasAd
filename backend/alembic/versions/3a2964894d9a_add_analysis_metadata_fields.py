"""add_analysis_metadata_fields

Revision ID: 3a2964894d9a
Revises: 012
Create Date: 2026-05-10 20:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a2964894d9a'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('analyses', sa.Column('author', sa.String(length=255), nullable=True))
    op.add_column('analyses', sa.Column('channel', sa.String(length=255), nullable=True))
    op.add_column('analyses', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('analyses', sa.Column('tonality', sa.String(length=50), nullable=True))
    op.add_column('analyses', sa.Column('categories', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('analyses', 'categories')
    op.drop_column('analyses', 'tonality')
    op.drop_column('analyses', 'published_at')
    op.drop_column('analyses', 'channel')
    op.drop_column('analyses', 'author')
