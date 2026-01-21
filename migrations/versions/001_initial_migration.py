"""Initial migration: ContactSubmission and TrialBooking models

Revision ID: 001
Revises: 
Create Date: 2026-01-21 14:55:07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Create initial database schema with contact_submissions and trial_bookings tables.
    
    Validates: Requirements 5.1, 5.2, 5.3
    """
    # Create contact_submissions table
    op.create_table(
        'contact_submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on submitted_at for contact_submissions
    op.create_index(
        'idx_submitted_at',
        'contact_submissions',
        ['submitted_at'],
        unique=False
    )
    
    # Create trial_bookings table
    op.create_table(
        'trial_bookings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('preferred_date', sa.Date(), nullable=False),
        sa.Column('preferred_time', sa.String(length=50), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create indexes for trial_bookings
    op.create_index(
        'idx_email',
        'trial_bookings',
        ['email'],
        unique=False
    )
    
    op.create_index(
        'idx_submitted_at',
        'trial_bookings',
        ['submitted_at'],
        unique=False
    )


def downgrade():
    """
    Drop all tables created in upgrade().
    """
    # Drop indexes first
    op.drop_index('idx_submitted_at', table_name='trial_bookings')
    op.drop_index('idx_email', table_name='trial_bookings')
    op.drop_index('idx_submitted_at', table_name='contact_submissions')
    
    # Drop tables
    op.drop_table('trial_bookings')
    op.drop_table('contact_submissions')
