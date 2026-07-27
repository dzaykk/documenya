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
    email: Email | None = None
    username: Username | None = None


class PasswordUpdate(BaseModel):
    current_password: Password
    new_password: Password