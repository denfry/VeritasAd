"""add_audit_logs_table

Revision ID: 005
Revises: 004
Create Date: 2026-02-18

BigTech standard audit logging table for compliance and security tracking.
Similar to AWS CloudTrail, Google Cloud Audit Logs, Azure Activity Log.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Create audit event type enum for PostgreSQL
    if dialect == 'postgresql':
        op.execute("""
            CREATE TYPE audit_event_type AS ENUM (
                -- Authentication
                'login', 'logout', 'login_failed', 'password_reset',
                'two_fa_enabled', 'two_fa_disabled',
                -- User management
                'user.created', 'user.updated', 'user.deleted',
                'user.banned', 'user.unbanned', 'user.activated', 'user.deactivated',
                'role.changed', 'plan.changed',
                -- Admin actions
                'admin.login', 'admin.logout', 'admin.user.view', 'admin.user.list',
                'admin.user.update', 'admin.analytics.view', 'admin.export', 'admin.impersonate',
                -- Data operations
                'data.export', 'data.import', 'data.delete',
                -- Security
                'session.revoked', 'api_key.created', 'api_key.revoked',
                'ip.whitelist.added', 'ip.whitelist.removed',
                -- System
                'settings.changed', 'permission.granted', 'permission.revoked'
            )
        """)
        event_type = sa.Enum(name='audit_event_type')
    else:
        # SQLite - use String
        event_type = sa.String(length=50)
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', event_type, nullable=False),
        sa.Column('event_category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('actor_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('actor_email', sa.String(length=255), nullable=True),
        sa.Column('actor_ip', sa.String(length=45), nullable=True),
        sa.Column('actor_user_agent', sa.String(length=500), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('target_email', sa.String(length=255), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'], unique=False)
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'], unique=False)
    op.create_index('ix_audit_logs_event_category', 'audit_logs', ['event_category'], unique=False)
    op.create_index('ix_audit_logs_actor_user_id', 'audit_logs', ['actor_user_id'], unique=False)
    op.create_index('ix_audit_logs_actor_email', 'audit_logs', ['actor_email'], unique=False)
    op.create_index('ix_audit_logs_status', 'audit_logs', ['status'], unique=False)
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    
    # Create composite indexes
    op.create_index(
        'idx_audit_logs_actor_created',
        'audit_logs',
        ['actor_user_id', 'created_at']
    )
    op.create_index(
        'idx_audit_logs_event_type_created',
        'audit_logs',
        ['event_type', 'created_at']
    )
    op.create_index(
        'idx_audit_logs_target',
        'audit_logs',
        ['target_type', 'target_id']
    )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Drop indexes
    op.drop_index('idx_audit_logs_target', table_name='audit_logs')
    op.drop_index('idx_audit_logs_event_type_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_actor_created', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_status', table_name='audit_logs')
    op.drop_index('ix_audit_logs_actor_email', table_name='audit_logs')
    op.drop_index('ix_audit_logs_actor_user_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_category', table_name='audit_logs')
    op.drop_index('ix_audit_logs_event_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_id', table_name='audit_logs')
    
    op.drop_table('audit_logs')
    
    # Drop enum type (PostgreSQL only)
    if dialect == 'postgresql':
        op.execute('DROP TYPE audit_event_type')
