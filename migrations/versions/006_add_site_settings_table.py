"""Add site_settings table

Revision ID: 006
Revises: 005
Create Date: 2026-01-21 19:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create site_settings table for managing site-wide visual elements.
    
    Stores configurable website elements including banner and logo image paths.
    Uses singleton pattern - only one row should exist (id=1).
    
    Validates: Requirements 16.6, 5.1
    """
    # Create site_settings table
    op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), nullable=False, default=1),
        sa.Column('banner_image_path', sa.String(length=255), nullable=True),
        sa.Column('logo_image_path', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='chk_singleton'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Insert default row with id=1 and NULL values for paths
    # This ensures the singleton row exists for the application to use
    op.execute(
        "INSERT INTO site_settings (id, banner_image_path, logo_image_path) "
        "VALUES (1, NULL, NULL)"
    )


def downgrade():
    """
    Drop site_settings table.
    """
    op.drop_table('site_settings')
