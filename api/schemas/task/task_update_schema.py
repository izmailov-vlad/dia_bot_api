from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from database.models.task.task_model import TaskStatusModel


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reminder: Optional[datetime] = None
    mark: Optional[str] = None
    status: Optional[TaskStatusModel] = None
