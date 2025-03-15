from datetime import datetime

from pydantic import BaseModel


class ReminderModel(BaseModel):
    time: datetime
    method: str  # "push" | "email" | "sms"