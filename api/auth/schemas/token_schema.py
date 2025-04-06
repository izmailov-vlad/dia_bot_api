from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str
