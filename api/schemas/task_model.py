import datetime
from typing import Optional
from pydantic import BaseModel


class DayTask(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class DailyPlan(BaseModel):
    tasks: list[DayTask]

    class Config:
        arbitrary_types_allowed = True
