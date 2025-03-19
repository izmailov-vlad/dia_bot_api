from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TaskSchemaCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
