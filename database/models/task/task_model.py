from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime
import enum

# Добавляем класс для Enum


class TaskStatusModel(enum.Enum):
    created = "created"
    completed = "completed"


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    reminder = Column(DateTime, nullable=True)
    mark = Column(String, nullable=True)
    status = Column(
        Enum(TaskStatusModel),
        nullable=False,
        default=TaskStatusModel.created,
    )
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
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("UserModel", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"
