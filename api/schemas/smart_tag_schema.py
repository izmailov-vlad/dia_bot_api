from pydantic import BaseModel, Field


class SmartTagSchema(BaseModel):
    id: str = Field(
        description="Уникальный идентификатор тега"
    )

    name: str = Field(
        description="Название тега"
    )

    class Config:
        from_attributes = True
