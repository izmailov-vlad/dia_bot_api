from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel
from api.schemas.range_filter import RangeFilter
from database.models.task.task_model import TaskStatus


class TaskFiltersModel(BaseModel):
    """Pydantic-модель, для фильтрации задач."""
    start_time: Optional[Union[datetime, RangeFilter]] = None
    end_time: Optional[Union[datetime, RangeFilter]] = None
    reminder: Optional[Union[datetime, RangeFilter]] = None
    mark: Optional[str] = None
    status: Optional[TaskStatus] = None

    class Config:
        # Запрещаем лишние поля (эквивалент additionalProperties=false)
        extra = "forbid"
