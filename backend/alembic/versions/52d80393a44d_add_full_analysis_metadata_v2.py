"""add_full_analysis_metadata_v2

Revision ID: 52d80393a44d
Revises: 1917a5633a69
Create Date: 2026-05-10 20:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52d80393a44d'
down_revision = '1917a5633a69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('author_username', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('channel_title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('detected_links', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('topics', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('sentiment_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('content_description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('engagement_metrics', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('risk_factors', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('compliance_flags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('recommendation', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('recommendation_confidence', sa.Float(), nullable=True))
        
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.drop_column('author')
        batch_op.drop_column('channel')


def downgrade() -> None:
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('channel', sa.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=255), nullable=True))

    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.drop_column('recommendation_confidence')
        batch_op.drop_column('recommendation')
        batch_op.drop_column('compliance_flags')
        batch_op.drop_column('risk_factors')
        batch_op.drop_column('engagement_metrics')
        batch_op.drop_column('content_description')
        batch_op.drop_column('sentiment_score')
        batch_op.drop_column('topics')
        batch_op.drop_column('detected_links')
        batch_op.drop_column('channel_title')
        batch_op.drop_column('author_username')
        batch_op.drop_column('author_name')
