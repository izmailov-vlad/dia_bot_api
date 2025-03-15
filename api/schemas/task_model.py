from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from api.schemas.recurrence_model import RecurrenceModel
from api.schemas.reminder_model import ReminderModel


class TaskModel(BaseModel):
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    priority: Optional[str]  # "low" | "medium" | "high" | "critical"
    category: Optional[str]
    status: str  # "planned" | "in_progress" | "completed" | "cancelled"
    location: Optional[str]
    reminders: Optional[List[ReminderModel]]
    recurrence: Optional[RecurrenceModel]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
        json_decoders={
            datetime: lambda v: datetime.fromisoformat(v),
        }
    )
