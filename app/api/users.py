from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserRead


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
):

    return current_user