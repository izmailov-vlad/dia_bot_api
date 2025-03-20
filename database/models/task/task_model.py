from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
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
    # user_id = Column(String, ForeignKey("users.id"), nullable=False)
    # user = relationship("User", back_populates="tasks")

    smart_tag_id = Column(String, ForeignKey('smart_tags.id'), nullable=True)
    smart_tag = relationship("SmartTagModel", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, user_id={self.user_id})>"
