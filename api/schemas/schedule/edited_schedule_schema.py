from pydantic import BaseModel

from api.schemas.schedule.edited_task_schema import EditedTaskSchema


class EditedScheduleSchema(BaseModel):
    tasks: list[EditedTaskSchema]
