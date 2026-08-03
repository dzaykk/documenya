from pydantic import BaseModel

from app.schemas.types_ import Email, Password


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    ver: int
    exp: int


class ReactivateRequest(BaseModel):
    email: Email
    password: Password