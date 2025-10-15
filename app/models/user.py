from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=True)
    motivations = Column(Text, nullable=True)
    language = Column(String(10), default="en")
    picture = Column(String(500), nullable=True)
    role = Column(String(20), default="user")  # 'user' or 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    moods = relationship("Mood", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="user", cascade="all, delete-orphan")


class Habit(Base):
    """Habit model for tracking user habits."""
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly
    description = Column(Text, nullable=True)
    streak_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="habits")


class MoodType(str, enum.Enum):
    """Enum for mood types."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    SAD = "sad"
    ANXIOUS = "anxious"
    ANGRY = "angry"


class Mood(Base):
    """Mood entry model for tracking user emotions."""
    __tablename__ = "moods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_type = Column(String(50), nullable=False)  # excellent, good, neutral, sad, anxious, angry
    intensity = Column(Integer, nullable=True)  # 1-10 scale
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="moods")


class Goal(Base):
    """Goal model for tracking user objectives."""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    goal_type = Column(String(100), nullable=False)  # fitness, mental, learning, etc.
    description = Column(Text, nullable=True)
    timeframe = Column(String(100), nullable=False)  # short-term, long-term, etc.
    completion_percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")


class Note(Base):
    """Note model for storing user notes."""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")


class ReminderType(str, enum.Enum):
    """Enum for reminder types."""
    HABIT = "habit"
    MEDITATION = "meditation"
    EXERCISE = "exercise"
    MINDFUL_EATING = "mindful_eating"
    BREAK = "break"
    CUSTOM = "custom"


class Reminder(Base):
    """Reminder model for scheduling notifications."""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reminder_type = Column(String(50), nullable=False)  # habit, meditation, exercise, mindful_eating, break, custom
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    trigger_time = Column(DateTime, nullable=False)
    frequency = Column(String(50), nullable=True)  # one-time, daily, weekly, etc.
    status = Column(String(20), default="pending")  # pending, triggered, completed, cancelled
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reminders")


class Analytics(Base):
    """Analytics model for storing user insights and progress."""
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary = Column(Text, nullable=False)
    score = Column(Float, nullable=False)  # Overall progress score
    mood_average = Column(Float, nullable=True)
    habit_completion_rate = Column(Float, nullable=True)
    goal_progress = Column(Float, nullable=True)
    insights = Column(Text, nullable=True)  # JSON string with detailed insights
    period = Column(String(50), nullable=False)  # daily, weekly, monthly
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analytics")
