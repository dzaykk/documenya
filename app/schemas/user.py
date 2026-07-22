from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.types import (
    Email,
    Password,
    Username,
)


class UserBase(BaseModel):
    email: Email
    username: Username


class UserCreate(UserBase):
    password: Password


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserUpdate(BaseModel):
    username: Username | None = None