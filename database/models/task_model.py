from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
import enum


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReminderMethod(enum.Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"


class RecurrenceFrequency(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    priority = Column(
        Enum(TaskPriority),
        nullable=True,
        default=TaskPriority.MEDIUM
    )
    category = Column(String, nullable=True)
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PLANNED
    )
    location = Column(String, nullable=True)

    # Храним reminders как JSON
    reminders = Column(JSON, nullable=True)

    # Храним recurrence как JSON
    recurrence = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now
    )

    # Отношение к пользователю
    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"
