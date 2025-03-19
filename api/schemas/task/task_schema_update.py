from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TaskSchemaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
