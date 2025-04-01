from pydantic import BaseModel

from api.schemas.task.task_response_schema import TaskResponseSchema


class EditedTaskSchema(BaseModel):
    action: str
    edited_task: TaskResponseSchema
