
from datetime import datetime
from pydantic import BaseModel, field_validator


class TimeRangeSchema(BaseModel):
    start_time: datetime
    end_time: datetime

    @field_validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    def __str__(self) -> str:
        return f"{self.start_time.isoformat()} - {self.end_time.isoformat()}"
