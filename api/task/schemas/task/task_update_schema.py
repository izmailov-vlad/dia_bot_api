from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from database.models.task.task_model import TaskStatusModel

class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    status: Optional[TaskStatusModel] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
