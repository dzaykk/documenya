from sqlalchemy.ext.asyncio import AsyncSession

from pwdlib import PasswordHash

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

from app.exceptions.auth import (
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    InvalidCredentials,
)


password_hash = PasswordHash.recommended()


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.user_repository = UserRepository(session)

    async def register(
        self,
        user_data: UserCreate,
    ) -> User:

        existing_user = await self.user_repository.get_by_email(
            user_data.email
        )

        if existing_user:
            raise EmailAlreadyRegistered()

        existing_username = await self.user_repository.get_by_username(
            user_data.username
        )

        if existing_username:
            raise UsernameAlreadyTaken()

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=self.hash_password(
                user_data.password
            ),
        )

        return await self.user_repository.create(user)


    def hash_password(
        self,
        password: str,
    ) -> str:

        return password_hash.hash(password)


    def verify_password(
        self,
        password: str,
        hashed_password: str,
    ) -> bool:

        return password_hash.verify(
            password,
            hashed_password,
        )


    async def authenticate(
        self,
        email: str,
        password: str,
    ) -> User | None:

        user = await self.user_repository.get_by_email(
            email
        )

        if not user:
            raise InvalidCredentials()

        if not self.verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentials()

        return user