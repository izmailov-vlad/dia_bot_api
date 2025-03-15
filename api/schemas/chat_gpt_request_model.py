from pydantic import BaseModel


class ChatGptRequestModel(BaseModel):
    message: str