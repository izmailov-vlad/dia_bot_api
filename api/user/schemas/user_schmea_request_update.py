from typing import Optional
from openai import BaseModel
from pydantic import Field


class UserSchemaRequestUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Имя пользователя",
    )
