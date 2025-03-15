from pydantic import BaseModel

from api.schemas.task_model import DayTask


class DailyPlanModel(BaseModel):
    tasks: list[DayTask]
