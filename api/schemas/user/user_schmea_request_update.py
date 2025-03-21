from openai import BaseModel


class UserSchemaRequestUpdate(BaseModel):
    username: str
