from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from database.database import Base
from datetime import datetime


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    telegram_id = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
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

    # Определение отношений
    tasks = relationship("TaskModel", back_populates="user")

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, telegram_id={self.telegram_id})>"
