from openai import BaseModel
from datetime import datetime


class UserSchemaResponse(BaseModel):
    id: str
    telegram_id: str
    username: str
    created_at: datetime
    updated_at: datetime
