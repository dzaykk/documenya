import logging

from app.core.security import (
    hash_password,
    verify_password,
)
from app.exceptions.auth import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    UsernameAlreadyTaken,
)
from app.models.user import User
from app.schemas.user import UserUpdate
from app.uow.base import AbstractUnitOfWork

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
    ):
        self.uow = uow

    async def update_profile(
        self,
        user: User,
        data: UserUpdate,
    ) -> User:

        logger.info(
            "Updating profile for user %s",
            user.id,
        )

        async with self.uow:

            if (
                data.username is not None
                and data.username != user.username
            ):

                existing = await self.uow.users.get_by_username(
                    data.username,
                )

                if existing:

                    logger.warning(
                        "Profile update failed: username '%s' already exists",
                        data.username,
                    )

                    raise UsernameAlreadyTaken()

                user.username = data.username

                logger.info(
                    "User %s changed username",
                    user.id,
                )

            if (
                data.email is not None
                and data.email != user.email
            ):

                existing = await self.uow.users.get_by_email(
                    data.email,
                )

                if existing:

                    logger.warning(
                        "Profile update failed: email '%s' already exists",
                        data.email,
                    )

                    raise EmailAlreadyRegistered()

                user.email = data.email

                logger.info(
                    "User %s changed email",
                    user.id,
                )

            user = await self.uow.users.update(
                user,
            )

            await self.uow.commit()

            logger.info(
                "Profile updated for user %s",
                user.id,
            )

            return user

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:

        logger.info(
            "Password change requested for user %s",
            user.id,
        )

        async with self.uow:

            if not verify_password(
                current_password,
                user.hashed_password,
            ):
                logger.warning(
                    "Password change failed for user %s: invalid current password",
                    user.id,
                )
                raise InvalidCredentials()

            user.hashed_password = hash_password(
                new_password,
            )

            user.token_version += 1

            await self.uow.users.update(
                user,
            )

            await self.uow.commit()

            logger.info(
                "Password changed for user %s",
                user.id,
            )

    async def deactivate(
        self,
        user: User,
    ) -> None:

        logger.info(
            "Deactivating user %s",
            user.id,
        )

        async with self.uow:

            if not user.is_active:

                logger.info(
                    "User %s is already deactivated",
                    user.id,
                )

                return

            user.is_active = False
            user.token_version += 1

            await self.uow.users.update(
                user,
            )

            await self.uow.commit()

            logger.info(
                "User %s deactivated",
                user.id,
            )