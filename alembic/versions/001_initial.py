"""Initial migration - create all tables.

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('gender', sa.String(50), nullable=True),
        sa.Column('motivations', sa.Text, nullable=True),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('picture', sa.String(500), nullable=True),
        sa.Column('role', sa.String(20), default='user'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create habits table
    op.create_table(
        'habits',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('streak_count', sa.Integer, default=0),
        sa.Column('success_rate', sa.Float, default=0.0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create moods table
    op.create_table(
        'moods',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('mood_type', sa.String(50), nullable=False),
        sa.Column('intensity', sa.Integer, nullable=True),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('goal_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('timeframe', sa.String(100), nullable=False),
        sa.Column('completion_percentage', sa.Float, default=0.0),
        sa.Column('is_completed', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_pinned', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reminder_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('trigger_time', sa.DateTime, nullable=False),
        sa.Column('frequency', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )
    
    # Create analytics table
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('score', sa.Float, nullable=False),
        sa.Column('mood_average', sa.Float, nullable=True),
        sa.Column('habit_completion_rate', sa.Float, nullable=True),
        sa.Column('goal_progress', sa.Float, nullable=True),
        sa.Column('insights', sa.Text, nullable=True),
        sa.Column('period', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('analytics')
    op.drop_table('reminders')
    op.drop_table('notes')
    op.drop_table('goals')
    op.drop_table('moods')
    op.drop_table('habits')
    op.drop_table('users')
