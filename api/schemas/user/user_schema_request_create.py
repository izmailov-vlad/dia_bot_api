from openai import BaseModel


class UserSchemaRequestCreate(BaseModel):
    telegram_id: str
    username: str
