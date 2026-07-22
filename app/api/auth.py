from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DBSession
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


OAuthForm = Annotated[
    OAuth2PasswordRequestForm,
    Depends(),
]


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: DBSession,
):
    service = AuthService(db)

    user = await service.register(user_data)

    return user


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    form_data: OAuthForm,
    db: DBSession,
):
    service = AuthService(db)

    user = await service.authenticate(
        form_data.username,
        form_data.password,
    )

    token = create_access_token(user.email)

    return Token(
        access_token=token,
        token_type="bearer",
    )