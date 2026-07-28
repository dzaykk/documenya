from unittest.mock import patch

import pytest

from app.exceptions.auth import (
    AccountAlreadyActiveError,
    AccountDeactivatedError,
    EmailAlreadyRegistered,
    InvalidCredentials,
    UsernameAlreadyTaken,
)
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


@pytest.fixture
def service(
    uow,
):
    return AuthService(
        uow,
    )


@pytest.mark.asyncio
async def test_register_success(
    service,
    uow,
):
    data = UserCreate(
        email="user@test.com",
        username="john",
        password="password123",
    )

    uow.users.get_by_email.return_value = None
    uow.users.get_by_username.return_value = None

    async def create_user(
        user,
    ):
        return user

    uow.users.create.side_effect = create_user

    with patch(
        "app.services.auth_service.hash_password",
        return_value="hashed-password",
    ):
        result = await service.register(
            data,
        )

    assert result.email == data.email
    assert result.username == data.username
    assert result.hashed_password == (
        "hashed-password"
    )

    uow.users.create.assert_awaited_once()

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_existing_email(
    service,
    uow,
    user,
):
    data = UserCreate(
        email=user.email,
        username="another",
        password="password123",
    )

    uow.users.get_by_email.return_value = user

    with pytest.raises(
        EmailAlreadyRegistered,
    ):
        await service.register(
            data,
        )

    uow.users.create.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_register_existing_username(
    service,
    uow,
    user,
):
    data = UserCreate(
        email="new@test.com",
        username=user.username,
        password="password123",
    )

    uow.users.get_by_email.return_value = None

    uow.users.get_by_username.return_value = user

    with pytest.raises(
        UsernameAlreadyTaken,
    ):
        await service.register(
            data,
        )

    uow.users.create.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_register_database_failure(
    service,
    uow,
):
    data = UserCreate(
        email="user@test.com",
        username="john",
        password="password123",
    )

    uow.users.get_by_email.return_value = None
    uow.users.get_by_username.return_value = None

    uow.users.create.side_effect = RuntimeError(
        "database error",
    )

    with patch(
        "app.services.auth_service.hash_password",
        return_value="hashed-password",
    ):
        with pytest.raises(
            RuntimeError,
        ):
            await service.register(
                data,
            )

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_success(
    service,
    uow,
    user,
):
    uow.users.get_by_login.return_value = user

    with patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    ):
        result = await service.authenticate(
            "john",
            "password123",
        )

    assert result is user


@pytest.mark.asyncio
async def test_authenticate_user_not_found(
    service,
    uow,
):
    uow.users.get_by_login.return_value = None

    with pytest.raises(
        InvalidCredentials,
    ):
        await service.authenticate(
            "missing",
            "password",
        )


@pytest.mark.asyncio
async def test_authenticate_invalid_password(
    service,
    uow,
    user,
):
    uow.users.get_by_login.return_value = user

    with patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(
            InvalidCredentials,
        ):
            await service.authenticate(
                "john",
                "wrong",
            )


@pytest.mark.asyncio
async def test_authenticate_deactivated_user(
    service,
    uow,
    inactive_user,
):
    uow.users.get_by_login.return_value = (
        inactive_user
    )

    with patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    ):
        with pytest.raises(
            AccountDeactivatedError,
        ):
            await service.authenticate(
                inactive_user.email,
                "password",
            )


@pytest.mark.asyncio
async def test_authenticate_inactive_user_invalid_password(
    service,
    uow,
    inactive_user,
):
    uow.users.get_by_login.return_value = (
        inactive_user
    )

    with patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(
            InvalidCredentials,
        ):
            await service.authenticate(
                inactive_user.email,
                "wrong",
            )


@pytest.mark.asyncio
async def test_reactivate_success(
    service,
    uow,
    inactive_user,
):
    uow.users.get_by_email.return_value = (
        inactive_user
    )

    uow.users.update.return_value = (
        inactive_user
    )

    old_version = (
        inactive_user.token_version
    )

    with patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    ):
        result = await service.reactivate(
            inactive_user.email,
            "password",
        )

    assert result is inactive_user

    assert inactive_user.is_active is True

    assert inactive_user.token_version == (
        old_version + 1
    )

    uow.users.update.assert_awaited_once_with(
        inactive_user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reactivate_user_not_found(
    service,
    uow,
):
    uow.users.get_by_email.return_value = None

    with pytest.raises(
        InvalidCredentials,
    ):
        await service.reactivate(
            "missing@test.com",
            "password",
        )

    uow.users.update.assert_not_called()


@pytest.mark.asyncio
async def test_reactivate_already_active(
    service,
    uow,
    user,
):
    uow.users.get_by_email.return_value = user

    with patch(
        "app.services.auth_service.verify_password",
        return_value=True,
    ):
        with pytest.raises(
            AccountAlreadyActiveError,
        ):
            await service.reactivate(
                user.email,
                "password",
            )


@pytest.mark.asyncio
async def test_reactivate_invalid_password(
    service,
    uow,
    inactive_user,
):
    uow.users.get_by_email.return_value = (
        inactive_user
    )

    with patch(
        "app.services.auth_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(
            InvalidCredentials,
        ):
            await service.reactivate(
                inactive_user.email,
                "wrong",
            )

    uow.users.update.assert_not_called()

    uow.commit.assert_not_called()