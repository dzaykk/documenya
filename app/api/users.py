from fastapi import (
    APIRouter,
    status,
)

from app.api.dependencies import (
    CurrentUser,
    UserServiceDep,
)
from app.schemas.user import (
    PasswordUpdate,
    UserRead,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    current_user: CurrentUser,
):
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    service: UserServiceDep,
):

    return await service.update_profile(
        current_user,
        data,
    )


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    data: PasswordUpdate,
    current_user: CurrentUser,
    service: UserServiceDep,
):

    await service.change_password(
        current_user,
        data.current_password,
        data.new_password,
    )


@router.post(
    "/me/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate current account",
)
async def deactivate_user(
    current_user: CurrentUser,
    service: UserServiceDep,
):

    await service.deactivate(
        current_user,
    )