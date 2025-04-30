from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from database.models.task.task_model import TaskStatusModel


class TaskResponseSchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    date: datetime
    status: TaskStatusModel

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
