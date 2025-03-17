from datetime import datetime

from pydantic import BaseModel


class ReminderSchema(BaseModel):
    time: datetime
    method: str  # "push" | "email" | "sms"
