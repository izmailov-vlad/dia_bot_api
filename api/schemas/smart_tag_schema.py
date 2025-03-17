from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, validator

from api.schemas.priority_schema import PrioritySchema
from api.schemas.recurrence_schema import RecurrenceSchema
from api.schemas.time_range_schema import TimeRangeSchema


class SmartTagModel(BaseModel):
    id: str = Field(
        description="Уникальный идентификатор тега"
    )

    name: str = Field(
        description="Название тега"
    )

    recommended_time: Optional[TimeRangeSchema] = Field(
        default=None,
        description="Рекомендуемый временной диапазон для выполнения задач с этим тегом (например, 9:00-17:00)"
    )

    default_duration: int = Field(
        default=60,
        description="Продолжительность задачи по умолчанию в минутах",
        ge=1  # greater or equal than 1
    )

    priority: PrioritySchema = Field(
        default=PrioritySchema.LOW,
        description="Приоритет задач с этим тегом (low, medium, high, critical)"
    )

    reminder: Optional[int] = Field(
        default=None,
        description="За сколько минут до начала задачи отправлять напоминание",
        ge=0  # greater or equal than 0
    )

    recurrence: Optional[RecurrenceSchema] = Field(
        default=None,
        description="Настройки повторения задач с этим тегом (ежедневно, еженедельно и т.д.)"
    )

    color: Optional[str] = Field(
        default="#FF5733",
        description="Цвет тега в HEX формате (#RRGGBB)",
        pattern="^#[0-9A-Fa-f]{6}$"  # валидация HEX цвета
    )

    daily_limit: Optional[int] = Field(
        default=None,
        description="Максимальное количество задач с этим тегом в день",
        ge=1  # greater or equal than 1
    )

    class Config:
        json_encoders = {
            TimeRangeSchema: str  # для корректной сериализации в JSON
        }
