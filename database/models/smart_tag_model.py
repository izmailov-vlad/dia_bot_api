from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from database.models.priority_model import PriorityModel


class SmartTag(Base):
    __tablename__ = "smart_tags"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    default_duration = Column(Integer, default=60)
    priority = Column(
        Enum(PriorityModel),
        nullable=True,
        default=PriorityModel.LOW
    )
    reminder = Column(Integer, nullable=True)
    color = Column(String, default="#FF5733")
    daily_limit = Column(Integer, nullable=True)

    # Отношения
    time_range = Column(String, ForeignKey('time_ranges.id'), nullable=True)
    recurrence = Column(String, ForeignKey('recurrences.id'), nullable=True)

    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)

    time_range = relationship("TimeRange")
    recurrence = relationship("Recurrence")
    task = relationship("Task", back_populates="smart_tags")
