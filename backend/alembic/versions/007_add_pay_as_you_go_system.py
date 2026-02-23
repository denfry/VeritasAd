"""add_pay_as_you_go_system

Revision ID: 007
Revises: 006
Create Date: 2026-02-18

Add pay-as-you-go credit system:
- user_credits: Store user credit balance
- credit_transactions: Transaction history for credits
- Update UserPlan enum with STARTER and BUSINESS tiers

Features:
- Users can purchase credit packages (micro, standard, pro, business)
- Credits are consumed when analysis is performed
- Credits have expiration dates based on package
- Full transaction history for auditing
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    
    # Step 1: Update UserPlan enum - add STARTER and BUSINESS
    # SQLite doesn't support ALTER TYPE, so we skip this for SQLite
    if dialect == 'postgresql':
        # Add new enum values to existing enum type
        op.execute("ALTER TYPE user_plan ADD VALUE IF NOT EXISTS 'starter'")
        op.execute("ALTER TYPE user_plan ADD VALUE IF NOT EXISTS 'business'")

    # Step 2: Create user_credits table
    op.create_table(
        'user_credits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_credits_id', 'user_credits', ['id'], unique=False)
    op.create_index('ix_user_credits_user_id', 'user_credits', ['user_id'], unique=False)
    op.create_index('ix_user_credits_created_at', 'user_credits', ['created_at'], unique=False)

    # Step 3: Create credit_transactions table
    op.create_table(
        'credit_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('package_type', sa.String(length=50), nullable=True),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('analysis_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_credit_transactions_id', 'credit_transactions', ['id'], unique=False)
    op.create_index('ix_credit_transactions_user_id', 'credit_transactions', ['user_id'], unique=False)
    op.create_index('ix_credit_transactions_created_at', 'credit_transactions', ['created_at'], unique=False)


def downgrade() -> None:
    # Step 1: Drop tables
    op.drop_table('credit_transactions')
    op.drop_table('user_credits')

    # Step 2: Revert enum (not directly possible in PostgreSQL)
    # For PostgreSQL, enum values cannot be removed easily
    # This is a limitation - you would need to recreate the type
