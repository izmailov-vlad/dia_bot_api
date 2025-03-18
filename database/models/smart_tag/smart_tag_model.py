from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class SmartTagModel(Base):
    __tablename__ = "smart_tags"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    default_duration = Column(Integer, default=60)
    reminder = Column(Integer, nullable=True)
    color = Column(String, default="#FF5733")
    daily_limit = Column(Integer, nullable=True)
    time_range = Column(String, ForeignKey('time_ranges.id'), nullable=True)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    task = relationship("Task", back_populates="smart_tags")
