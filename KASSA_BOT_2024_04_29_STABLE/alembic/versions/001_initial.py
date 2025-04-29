"""initial

Revision ID: 001
Revises: 
Create Date: 2024-03-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем таблицу users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('telegram_id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('avatar', sa.String(), nullable=True),
        sa.Column('user_link', sa.String(), nullable=True),
        sa.Column('referral_id', sa.String(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, default=1),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['referral_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Создаем таблицу referral_circles
    op.create_table(
        'referral_circles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('owner_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('referrals_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_id')
    )
    op.create_index(op.f('ix_referral_circles_id'), 'referral_circles', ['id'], unique=False)

    # Создаем таблицу referrals
    op.create_table(
        'referrals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('circle_id', sa.String(), nullable=False),
        sa.Column('referral_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['circle_id'], ['referral_circles.id'], ),
        sa.ForeignKeyConstraint(['referral_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referrals_id'), 'referrals', ['id'], unique=False)

    # Создаем таблицу referral_history
    op.create_table(
        'referral_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('circle_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['circle_id'], ['referral_circles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referral_history_id'), 'referral_history', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_referral_history_id'), table_name='referral_history')
    op.drop_table('referral_history')
    
    op.drop_index(op.f('ix_referrals_id'), table_name='referrals')
    op.drop_table('referrals')
    
    op.drop_index(op.f('ix_referral_circles_id'), table_name='referral_circles')
    op.drop_table('referral_circles')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users') 