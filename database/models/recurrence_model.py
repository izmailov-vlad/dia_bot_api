from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
from database.models.frequency_model import FrequencyModel

"""
Модель для описания повторяющихся задач.
"""


class Recurrence(Base):
    __tablename__ = "recurrences"

    id = Column(String, primary_key=True)
    frequency = Column(Enum(FrequencyModel), nullable=False)
    interval = Column(Integer, nullable=False)
    end_date = Column(DateTime, nullable=True)
    task_id = Column(String, ForeignKey('tasks.id'))

    task = relationship("Task", back_populates="recurrence")
