"""Add FAQs table

Revision ID: 004
Revises: 003
Create Date: 2026-01-21 17:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create FAQs table for storing frequently asked questions.
    
    Validates: Requirements 11.5, 5.1
    """
    # Create faqs table
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on display_order for query performance
    # This index helps when querying FAQs in display order
    op.create_index(
        'idx_display_order',
        'faqs',
        ['display_order'],
        unique=False
    )


def downgrade():
    """
    Drop FAQs table and its indexes.
    """
    # Drop index first
    op.drop_index('idx_display_order', table_name='faqs')
    
    # Drop table
    op.drop_table('faqs')
