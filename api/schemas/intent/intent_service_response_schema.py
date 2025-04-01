from pydantic import BaseModel


class IntentServiceResponseSchema(BaseModel):
    delegate_to: str
