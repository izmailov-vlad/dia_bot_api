from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field

from api.schemas.task.task_status_schema import TaskStatusSchema


class DateTimeRange(BaseModel):
    gte: Optional[datetime] = Field(
        None,
        description="Greater than or equal to",
    )
    lte: Optional[datetime] = Field(None, description="Less than or equal to")


class TaskFilterSchema(BaseModel):
    start_time: Optional[Union[datetime, DateTimeRange]] = None
    end_time: Optional[Union[datetime, DateTimeRange]] = None
    reminder: Optional[Union[datetime, DateTimeRange]] = None
    mark: Optional[str] = None
    status: Optional[TaskStatusSchema] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "start_time": "2024-03-20T10:00:00",
                    "end_time": {
                        "gte": "2024-03-20T12:00:00",
                        "lte": "2024-03-20T18:00:00"
                    },
                    "reminder": "2024-03-20T09:45:00",
                    "mark": "work",
                    "status": "created"
                }
            ]
        }
    }
