from sqlalchemy import Column, String, DateTime
from database.database import Base


class TimeRange(Base):
    __tablename__ = "time_ranges"

    id = Column(String, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
