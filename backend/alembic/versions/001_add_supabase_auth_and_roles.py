"""add_supabase_auth_and_roles

Revision ID: 001
Revises:
Create Date: 2026-01-24

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get the dialect to determine database type
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Create user_role enum type for PostgreSQL
    if dialect == 'postgresql':
        # Check if enum type already exists
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'user_role'")
        )
        if result.fetchone() is None:
            op.execute("CREATE TYPE user_role AS ENUM ('user', 'admin')")
        
        # Create user_plan enum type for PostgreSQL
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'user_plan'")
        )
        if result.fetchone() is None:
            op.execute("CREATE TYPE user_plan AS ENUM ('free', 'starter', 'pro', 'business', 'enterprise')")
        
        # Create source_type enum type for PostgreSQL
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'source_type'")
        )
        if result.fetchone() is None:
            op.execute("""
                CREATE TYPE source_type AS ENUM (
                    'file', 'url', 'youtube', 'telegram', 
                    'instagram', 'tiktok', 'vk'
                )
            """)
        
        # Create analysis_status enum type for PostgreSQL
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'analysis_status'")
        )
        if result.fetchone() is None:
            op.execute("""
                CREATE TYPE analysis_status AS ENUM (
                    'pending', 'queued', 'processing', 'completed', 'failed'
                )
            """)
        
        # Create payment_status enum type for PostgreSQL
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'payment_status'")
        )
        if result.fetchone() is None:
            op.execute("""
                CREATE TYPE payment_status AS ENUM (
                    'pending', 'succeeded', 'canceled', 'failed'
                )
            """)
        
        # Create payment_provider enum type for PostgreSQL
        result = bind.execute(
            sa.text("SELECT 1 FROM pg_type WHERE typname = 'payment_provider'")
        )
        if result.fetchone() is None:
            op.execute("""
                CREATE TYPE payment_provider AS ENUM ('yookassa')
            """)
    
    # Define enum types for SQLAlchemy
    if dialect == 'postgresql':
        role_type = sa.Enum('user', 'admin', name='user_role')
        plan_type = sa.Enum('free', 'starter', 'pro', 'business', 'enterprise', name='user_plan')
        source_type = sa.Enum('file', 'url', 'youtube', 'telegram', 'instagram', 'tiktok', 'vk', name='source_type')
        analysis_status_type = sa.Enum('pending', 'queued', 'processing', 'completed', 'failed', name='analysis_status')
        payment_status_type = sa.Enum('pending', 'succeeded', 'canceled', 'failed', name='payment_status')
        payment_provider_type = sa.Enum('yookassa', name='payment_provider')
    else:
        # For SQLite, use String
        role_type = sa.String(length=10)
        plan_type = sa.String(length=20)
        source_type = sa.String(length=20)
        analysis_status_type = sa.String(length=20)
        payment_status_type = sa.String(length=20)
        payment_provider_type = sa.String(length=20)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key_hash', sa.String(length=64), nullable=True),
        sa.Column('api_key_encrypted', sa.String(length=255), nullable=True),
        sa.Column('supabase_user_id', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('telegram_id', sa.Integer(), nullable=True),
        sa.Column('telegram_username', sa.String(length=256), nullable=True),
        sa.Column('telegram_link_token', sa.String(length=64), nullable=True),
        sa.Column('telegram_linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('plan', plan_type, nullable=False, server_default='free'),
        sa.Column('role', role_type, nullable=False, server_default='user'),
        sa.Column('daily_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('daily_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reset_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_analyses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for users
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_api_key_hash', 'users', ['api_key_hash'], unique=True)
    op.create_index('ix_users_supabase_user_id', 'users', ['supabase_user_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=False)
    op.create_index('ix_users_telegram_link_token', 'users', ['telegram_link_token'], unique=True)
    
    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('video_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('source_url', sa.String(length=2000), nullable=True),
        sa.Column('source_type', source_type, nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('file_path', sa.String(length=1000), nullable=True),
        sa.Column('has_advertising', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('visual_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('audio_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('text_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('disclosure_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('detected_brands', sa.JSON(), nullable=True),
        sa.Column('detected_keywords', sa.JSON(), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('disclosure_markers', sa.JSON(), nullable=True),
        sa.Column('ad_classification', sa.String(length=32), nullable=True),
        sa.Column('ad_reason', sa.Text(), nullable=True),
        sa.Column('status', analysis_status_type, nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('report_path', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for analyses
    op.create_index('ix_analyses_id', 'analyses', ['id'], unique=False)
    op.create_index('ix_analyses_task_id', 'analyses', ['task_id'], unique=True)
    op.create_index('ix_analyses_video_id', 'analyses', ['video_id'], unique=True)
    op.create_index('ix_analyses_user_id', 'analyses', ['user_id'], unique=False)
    op.create_index('ix_analyses_status', 'analyses', ['status'], unique=False)
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False, server_default='RUB'),
        sa.Column('status', payment_status_type, nullable=False),
        sa.Column('provider', payment_provider_type, nullable=False),
        sa.Column('provider_payment_id', sa.String(length=255), nullable=True),
        sa.Column('payment_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for payments
    op.create_index('ix_payments_id', 'payments', ['id'], unique=False)
    op.create_index('ix_payments_user_id', 'payments', ['user_id'], unique=False)
    op.create_index('ix_payments_status', 'payments', ['status'], unique=False)


def downgrade() -> None:
    # Get the dialect to determine database type
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Drop tables
    op.drop_table('payments')
    op.drop_table('analyses')
    op.drop_table('users')
    
    # Drop enum types (PostgreSQL only)
    if dialect == 'postgresql':
        op.execute("DROP TYPE IF EXISTS user_role")
        op.execute("DROP TYPE IF EXISTS user_plan")
        op.execute("DROP TYPE IF EXISTS source_type")
        op.execute("DROP TYPE IF EXISTS analysis_status")
        op.execute("DROP TYPE IF EXISTS payment_status")
        op.execute("DROP TYPE IF EXISTS payment_provider")
