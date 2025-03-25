from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from database.models.task.task_model import TaskStatus


class TaskSchemaResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    reminder: Optional[datetime]
    mark: Optional[str]
    status: TaskStatus
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
        json_decoders={
            datetime: lambda v: datetime.fromisoformat(v),
        }
    )
