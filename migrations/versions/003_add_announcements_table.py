"""Add announcements table

Revision ID: 003
Revises: 002
Create Date: 2026-01-21 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create announcements table for storing school announcements.
    
    Validates: Requirements 11, 5.1
    """
    # Create announcements table
    op.create_table(
        'announcements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('published_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on published_date for query performance
    # This index helps when querying announcements in reverse chronological order
    op.create_index(
        'idx_published_date',
        'announcements',
        ['published_date'],
        unique=False
    )


def downgrade():
    """
    Drop announcements table and its indexes.
    """
    # Drop index first
    op.drop_index('idx_published_date', table_name='announcements')
    
    # Drop table
    op.drop_table('announcements')
