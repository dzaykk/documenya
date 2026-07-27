import logging

from app.core.security import (
    hash_password,
    verify_password,
)

from app.exceptions.auth import (
    AccountAlreadyActiveError,
    AccountDeactivatedError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    UsernameAlreadyTaken,
)

from app.models.user import User

from app.schemas.user import UserCreate

from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ):
        self.uow = uow

    async def register(
        self,
        user_data: UserCreate,
    ) -> User:

        logger.info(
            "Registration attempt for email '%s'",
            user_data.email,
        )

        async with self.uow:

            existing_user = await self.uow.users.get_by_email(
                user_data.email,
            )

            if existing_user:

                logger.warning(
                    "Registration failed: email '%s' already exists",
                    user_data.email,
                )

                raise EmailAlreadyRegistered()

            existing_username = await self.uow.users.get_by_username(
                user_data.username,
            )

            if existing_username:

                logger.warning(
                    "Registration failed: username '%s' already exists",
                    user_data.username,
                )

                raise UsernameAlreadyTaken()

            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hash_password(
                    user_data.password,
                ),
            )

            user = await self.uow.users.create(
                user,
            )

            await self.uow.commit()

            logger.info(
                "User %s registered",
                user.id,
            )

            return user

    async def authenticate(
        self,
        login: str,
        password: str,
    ) -> User:

        logger.info(
            "Authentication attempt for '%s'",
            login,
        )

        async with self.uow:

            user = await self.uow.users.get_by_login(
                login,
            )

            if user is None:

                logger.warning(
                    "Authentication failed for '%s': user not found",
                    login,
                )

                raise InvalidCredentials()

            if not verify_password(
                password,
                user.hashed_password,
            ):

                logger.warning(
                    "Authentication failed for '%s': invalid password",
                    login,
                )

                raise InvalidCredentials()

            if not user.is_active:

                logger.warning(
                    "Authentication failed: user %s is deactivated",
                    user.id,
                )

                raise AccountDeactivatedError()

            logger.info(
                "User %s authenticated",
                user.id,
            )

            return user

    async def reactivate(
        self,
        email: str,
        password: str,
    ) -> User:

        logger.info(
            "Reactivation attempt for '%s'",
            email,
        )

        async with self.uow:

            user = await self.uow.users.get_by_email(
                email,
            )

            if user is None:

                logger.warning(
                    "Reactivation failed: user '%s' not found",
                    email,
                )

                raise InvalidCredentials()

            if not verify_password(
                password,
                user.hashed_password,
            ):

                logger.warning(
                    "Reactivation failed: invalid password for '%s'",
                    email,
                )

                raise InvalidCredentials()

            if user.is_active:

                logger.warning(
                    "Reactivation failed: user %s is already active",
                    user.id,
                )

                raise AccountAlreadyActiveError()

            user.is_active = True
            user.token_version += 1

            user = await self.uow.users.update(
                user,
            )

            await self.uow.commit()

            logger.info(
                "User %s reactivated",
                user.id,
            )

            return user