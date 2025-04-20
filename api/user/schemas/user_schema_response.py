from pydantic import BaseModel
from datetime import datetime


class UserSchemaResponse(BaseModel):
    id: str
    email: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
