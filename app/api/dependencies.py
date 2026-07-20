from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.core.security import decode_access_token

from app.services.document_service import DocumentService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


async def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: DBSession,
):

    email = decode_access_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    repository = UserRepository(db)

    user = await repository.get_by_email(
        email
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    return DocumentService(db)