from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RangeFilter(BaseModel):
    """Модель для хранения диапазона дат/времени (gte / lte)."""
    gte: Optional[datetime] = None
    lte: Optional[datetime] = None

    class Config:
        # Запрещаем лишние поля (эквивалент additionalProperties=false)
        extra = "forbid"
