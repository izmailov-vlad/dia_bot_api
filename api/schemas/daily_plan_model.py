from pydantic import BaseModel

from api.schemas.task_model import TaskModel


class DailyPlanModel(BaseModel):
    tasks: list[TaskModel]

    class Config:
        arbitrary_types_allowed = True
