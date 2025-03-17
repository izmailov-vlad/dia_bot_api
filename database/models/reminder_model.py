from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(String, primary_key=True)
    time = Column(DateTime, nullable=False)
    method = Column(String, nullable=False)  # "push", "email", "sms"
    task_id = Column(String, ForeignKey('tasks.id'))

    task = relationship("Task", back_populates="reminders")
