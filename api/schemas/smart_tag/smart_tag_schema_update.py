from pydantic import BaseModel
from typing import Optional


class SmartTagSchemaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
