"""add_telegram_integration_fields

Revision ID: 006
Revises: 005
Create Date: 2026-02-18

Add Telegram integration fields to users table:
- telegram_username: Store Telegram username
- telegram_link_token: Unique token for linking accounts
- telegram_linked_at: Timestamp when account was linked

These fields enable:
- Telegram Login Widget authentication
- Account linking between website and Telegram bot
- Unified user experience across platforms
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    insp = inspect(bind)
    columns = [col['name'] for col in insp.get_columns('users')]

    # Add telegram_username column if not exists
    if 'telegram_username' not in columns:
        if dialect == 'postgresql':
            op.add_column('users', sa.Column('telegram_username', sa.String(length=256), nullable=True))
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.add_column(sa.Column('telegram_username', sa.String(length=256), nullable=True))

    # Add telegram_link_token column if not exists
    if 'telegram_link_token' not in columns:
        if dialect == 'postgresql':
            op.add_column('users', sa.Column('telegram_link_token', sa.String(length=64), nullable=True))
            # Create unique constraint
            op.create_unique_constraint('uq_users_telegram_link_token', 'users', ['telegram_link_token'])
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.add_column(sa.Column('telegram_link_token', sa.String(length=64), nullable=True))

    # Add telegram_linked_at column if not exists
    if 'telegram_linked_at' not in columns:
        if dialect == 'postgresql':
            op.add_column('users', sa.Column('telegram_linked_at', sa.DateTime(timezone=True), nullable=True))
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.add_column(sa.Column('telegram_linked_at', sa.DateTime(timezone=True), nullable=True))

    # Create index on telegram_id for faster lookups if not exists
    if dialect == 'postgresql':
        result = bind.execute(sa.text("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'users' AND indexname = 'ix_users_telegram_id'
        """))
        if result.fetchone() is None:
            op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=False)
    else:
        try:
            op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=False)
        except Exception:
            pass  # Index already exists


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    insp = inspect(bind)
    columns = [col['name'] for col in insp.get_columns('users')]

    # Drop index
    op.drop_index('ix_users_telegram_id', table_name='users')

    # Drop columns in reverse order
    if 'telegram_linked_at' in columns:
        if dialect == 'postgresql':
            op.drop_column('users', 'telegram_linked_at')
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.drop_column('telegram_linked_at')

    if 'telegram_link_token' in columns:
        if dialect == 'postgresql':
            op.drop_constraint('uq_users_telegram_link_token', 'users', type_='unique')
            op.drop_column('users', 'telegram_link_token')
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.drop_column('telegram_link_token')

    if 'telegram_username' in columns:
        if dialect == 'postgresql':
            op.drop_column('users', 'telegram_username')
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.drop_column('telegram_username')
