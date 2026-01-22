"""Add classes table

Revision ID: 002
Revises: 001
Create Date: 2026-01-21 15:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create classes table for storing scheduled training sessions.
    
    Validates: Requirements 10, 5.1
    """
    # Create classes table
    op.create_table(
        'classes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('day_of_week', sa.String(length=20), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on day_of_week for query performance
    # This index helps when querying classes by day for display
    op.create_index(
        'idx_day_of_week',
        'classes',
        ['day_of_week'],
        unique=False
    )


def downgrade():
    """
    Drop classes table and its indexes.
    """
    # Drop index first
    op.drop_index('idx_day_of_week', table_name='classes')
    
    # Drop table
    op.drop_table('classes')
