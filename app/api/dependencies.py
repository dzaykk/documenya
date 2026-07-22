from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.exceptions.auth import (
    InvalidTokenError,
    UserNotFoundError,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]



async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> User:

    email = decode_access_token(token)

    if not email:
        raise InvalidTokenError()

    repository = UserRepository(db)

    user = await repository.get_by_email(email)

    if not user:
        raise UserNotFoundError()

    return user


def get_document_service(
    db: DBSession,
) -> DocumentService:
    return DocumentService(db)



CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]

DocumentServiceDep = Annotated[
    DocumentService,
    Depends(get_document_service),
]