from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        user: User,
    ) -> User:
        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user