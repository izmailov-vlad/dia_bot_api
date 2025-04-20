from pydantic import BaseModel, EmailStr


class AuthLoginSchema(BaseModel):
    email: EmailStr
    password: str
