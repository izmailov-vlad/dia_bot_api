from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskResponseSchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    date: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    reminder: Optional[datetime]
    mark: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
        json_decoders={
            datetime: lambda v: datetime.fromisoformat(v),
        }
    )
