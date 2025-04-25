from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from api.task.schemas.task.task_response_schema import TaskResponseSchema


class TasksResponseSchema(BaseModel):
    """Схема ответа со списком задач"""
    tasks: List[TaskResponseSchema]

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
        json_decoders={
            datetime: lambda v: datetime.fromisoformat(v),
        }
    )
