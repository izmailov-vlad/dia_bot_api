from pydantic import BaseModel


class SmartTagSchemaCreate(BaseModel):
    name: str
    description: str
