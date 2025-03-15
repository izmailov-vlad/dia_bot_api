from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RecurrenceModel(BaseModel):
    frequency: str  # "daily" | "weekly" | "monthly" | "yearly"
    interval: int
    end_date: Optional[datetime]
