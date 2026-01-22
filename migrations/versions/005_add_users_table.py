"""Add users table

Revision ID: 005
Revises: 004
Create Date: 2026-01-21 18:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create users table for instructor authentication.
    
    Stores instructor user accounts with username, password hash, and email.
    Passwords are hashed using bcrypt via Werkzeug's security utilities.
    
    Validates: Requirements 12.6, 5.1
    """
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='uq_username'),
        sa.UniqueConstraint('email', name='uq_email'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on username for login queries
    # This index helps when authenticating users by username
    op.create_index(
        'idx_username',
        'users',
        ['username'],
        unique=False
    )
    
    # Create index on email for lookup queries
    # This index helps when looking up users by email
    op.create_index(
        'idx_email',
        'users',
        ['email'],
        unique=False
    )


def downgrade():
    """
    Drop users table and its indexes.
    """
    # Drop indexes first
    op.drop_index('idx_email', table_name='users')
    op.drop_index('idx_username', table_name='users')
    
    # Drop table
    op.drop_table('users')
