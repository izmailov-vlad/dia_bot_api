from openai import BaseModel
from pydantic import Field


class UserSchemaRequestCreate(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID пользователя")
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя пользователя",
    )
