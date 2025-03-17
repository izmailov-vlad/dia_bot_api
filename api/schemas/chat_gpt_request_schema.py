from pydantic import BaseModel


class ChatGptRequestSchema(BaseModel):
    message: str
