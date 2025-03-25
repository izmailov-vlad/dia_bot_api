from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from database.models.task.task_model import TaskStatus


class TaskSchemaCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reminder: Optional[datetime] = None
    mark: Optional[str] = None
    status: TaskStatus = TaskStatus.created
