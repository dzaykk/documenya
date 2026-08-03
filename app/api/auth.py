from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    AuthServiceDep,
)
from app.core.security import (
    create_access_token,
)
from app.schemas.auth import (
    ReactivateRequest,
    Token,
)
from app.schemas.user import (
    UserCreate,
    UserRead,
)

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
    service: AuthServiceDep,
):

    return await service.register(
        user_data,
    )


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    form_data: OAuthForm,
    service: AuthServiceDep,
):

    user = await service.authenticate(
        form_data.username,
        form_data.password,
    )

    token = create_access_token(
        user.id,
        user.token_version,
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )


@router.post(
    "/reactivate",
    response_model=Token,
    summary="Reactivate account",
)
async def reactivate(
    data: ReactivateRequest,
    service: AuthServiceDep,
):

    user = await service.reactivate(
        data.email,
        data.password,
    )

    token = create_access_token(
        user.id,
        user.token_version,
    )

    return Token(
        access_token=token,
        token_type="bearer",
    )