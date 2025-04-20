from pydantic import BaseModel, EmailStr, model_validator


class AuthRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(cls, values):
        if values.password != values.confirm_password:
            raise ValueError("Пароли не совпадают")
        return values
