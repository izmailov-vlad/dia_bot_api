from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from database.models.task.task_model import TaskStatusModel


class TaskCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reminder: Optional[datetime] = None
    mark: Optional[str] = None
    status: TaskStatusModel = TaskStatusModel.created
