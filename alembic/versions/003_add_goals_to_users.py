"""Add goals column to users table

Revision ID: 003_add_goals_to_users
Revises: 002_add_new_tables
Create Date: 2025-11-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '003_add_goals_to_users'
down_revision = '002_add_new_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user_goals column to users table
    op.add_column('users', sa.Column('user_goals', JSON, nullable=True))


def downgrade() -> None:
    # Remove user_goals column from users table
    op.drop_column('users', 'user_goals')
