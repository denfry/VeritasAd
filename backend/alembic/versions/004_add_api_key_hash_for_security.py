"""add_api_key_hash_for_security

Revision ID: 004
Revises: 003
Create Date: 2024-01-01

Security migration: Add API key hash column for secure storage
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    insp = inspect(bind)
    columns = [col['name'] for col in insp.get_columns('users')]
    
    # Add new columns for secure API key storage if they don't exist
    if 'api_key_hash' not in columns:
        op.add_column('users', sa.Column('api_key_hash', sa.String(64), nullable=True))
    
    if 'api_key_encrypted' not in columns:
        op.add_column('users', sa.Column('api_key_encrypted', sa.String(255), nullable=True))

    # Create unique index on api_key_hash for fast lookups if it doesn't exist
    if dialect == 'postgresql':
        # Check if index exists
        result = bind.execute(sa.text("""
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'users' AND indexname = 'ix_users_api_key_hash'
        """))
        if result.fetchone() is None:
            op.create_index('ix_users_api_key_hash', 'users', ['api_key_hash'], unique=True)
    else:
        # SQLite - try to create index, ignore if exists
        try:
            op.create_index('ix_users_api_key_hash', 'users', ['api_key_hash'], unique=True)
        except Exception:
            pass  # Index already exists

    # Note: Existing api_key column is kept for backward compatibility
    # It should be removed in a future migration after all keys are migrated


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    insp = inspect(bind)
    columns = [col['name'] for col in insp.get_columns('users')]
    
    op.drop_index('ix_users_api_key_hash', table_name='users')
    
    if 'api_key_encrypted' in columns:
        if dialect == 'postgresql':
            op.drop_column('users', 'api_key_encrypted')
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.drop_column('api_key_encrypted')
    
    if 'api_key_hash' in columns:
        if dialect == 'postgresql':
            op.drop_column('users', 'api_key_hash')
        else:
            with op.batch_alter_table('users', schema=None) as batch_op:
                batch_op.drop_column('api_key_hash')
