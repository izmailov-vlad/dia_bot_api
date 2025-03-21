from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class SmartTagModel(Base):
    __tablename__ = "smart_tags"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
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
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    user = relationship("UserModel", back_populates="smart_tags")

    tasks = relationship("TaskModel", back_populates="smart_tag")
