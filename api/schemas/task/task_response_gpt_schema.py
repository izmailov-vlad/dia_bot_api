from openai import BaseModel
from datetime import datetime


class TaskResponseGptSchema(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
