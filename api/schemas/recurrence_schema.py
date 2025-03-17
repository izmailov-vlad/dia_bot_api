from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurrenceSchema(BaseModel):
    frequency: RecurrenceFrequency
    interval: int
    end_date: Optional[datetime] = None
