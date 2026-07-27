import logging

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db

from app.exceptions.auth import (
    AccountDeactivatedError,
    InvalidTokenError,
    UserNotFoundError,
)

from app.models.user import User

from app.repositories.user_repository import UserRepository

from app.services.auth_service import AuthService
from app.services.document_parser_service import (
    DocumentParserService,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.services.document_service import (
    DocumentService,
)
from app.services.user_service import UserService

from app.storage.service import StorageService

from app.uow.sqlalchemy import SQLAlchemyUnitOfWork

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_uow(
    db: DBSession,
) -> SQLAlchemyUnitOfWork:

    return SQLAlchemyUnitOfWork(
        db,
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> User:

    payload = decode_access_token(
        token,
    )

    if payload is None:

        logger.warning(
            "Invalid access token",
        )

        raise InvalidTokenError()

    user_id, token_version = payload

    repository = UserRepository(
        db,
    )

    user = await repository.get_by_id(
        user_id,
    )

    if user is None:

        logger.warning(
            "User %s from token not found",
            user_id,
        )

        raise UserNotFoundError()

    if user.token_version != token_version:

        logger.warning(
            "Revoked token used by user %s",
            user.id,
        )

        raise InvalidTokenError()

    if not user.is_active:

        logger.warning(
            "Inactive user %s tried to access API",
            user.id,
        )

        raise AccountDeactivatedError()

    return user


def get_auth_service(
    uow: Annotated[
        SQLAlchemyUnitOfWork,
        Depends(get_uow),
    ],
) -> AuthService:

    return AuthService(
        uow,
    )


def get_user_service(
    uow: Annotated[
        SQLAlchemyUnitOfWork,
        Depends(get_uow),
    ],
) -> UserService:

    return UserService(
        uow,
    )


def get_document_service(
    uow: Annotated[
        SQLAlchemyUnitOfWork,
        Depends(get_uow),
    ],
) -> DocumentService:

    return DocumentService(
        uow=uow,
        storage_service=StorageService(),
    )


def get_document_parser_service() -> DocumentParserService:

    return DocumentParserService()


def get_document_processing_service(
    uow: Annotated[
        SQLAlchemyUnitOfWork,
        Depends(get_uow),
    ],
    parser: Annotated[
        DocumentParserService,
        Depends(get_document_parser_service),
    ],
) -> DocumentProcessingService:

    return DocumentProcessingService(
        uow=uow,
        parser=parser,
    )


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


DocumentServiceDep = Annotated[
    DocumentService,
    Depends(get_document_service),
]


DocumentProcessingServiceDep = Annotated[
    DocumentProcessingService,
    Depends(get_document_processing_service),
]