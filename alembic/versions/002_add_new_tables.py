"""Add assessment and personal inspiration tables

Revision ID: 002_add_new_tables
Revises: 001_initial
Create Date: 2025-11-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '002_add_new_tables'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assessment_name', sa.String(255), nullable=False),
        sa.Column('assessment_type', sa.String(100), nullable=False),
        sa.Column('questions', JSON, nullable=False),
        sa.Column('results', JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create personal_inspirations table
    op.create_table(
        'personal_inspirations',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('inspiration', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('personal_inspirations')
    op.drop_table('assessments')
