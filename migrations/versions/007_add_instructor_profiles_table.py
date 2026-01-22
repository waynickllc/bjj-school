"""Add instructor_profiles table

Revision ID: 007
Revises: 006
Create Date: 2026-01-21 20:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create instructor_profiles table for managing instructor information.
    
    Stores instructor profile details including photo, biography, title/designation,
    and head instructor status. Each profile is linked to a User account via foreign key.
    Only one instructor can be designated as head instructor at a time.
    
    The biography length constraint (10-5000 characters) is enforced at the application
    level in form validation rather than at the database level to maintain compatibility
    with SQLite for testing. In production MySQL, this constraint can be added via
    CHECK constraint.
    
    Validates: Requirements 17, 5.1
    """
    # Create instructor_profiles table
    op.create_table(
        'instructor_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('photo_path', sa.String(length=255), nullable=True),
        sa.Column('biography', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('is_head_instructor', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_instructor_profiles_user_id',
            ondelete='CASCADE'
        ),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # Create index on user_id for foreign key lookups
    # This index helps when querying profiles by user
    op.create_index(
        'idx_user_id',
        'instructor_profiles',
        ['user_id'],
        unique=False
    )
    
    # Create index on is_head_instructor for finding head instructor
    # This index helps when querying for the head instructor
    op.create_index(
        'idx_is_head_instructor',
        'instructor_profiles',
        ['is_head_instructor'],
        unique=False
    )


def downgrade():
    """
    Drop instructor_profiles table and its indexes.
    """
    # Drop indexes first
    op.drop_index('idx_is_head_instructor', table_name='instructor_profiles')
    op.drop_index('idx_user_id', table_name='instructor_profiles')
    
    # Drop table (foreign key constraint will be dropped automatically)
    op.drop_table('instructor_profiles')
