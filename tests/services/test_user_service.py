from unittest.mock import patch

import pytest

from app.exceptions.auth import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    UsernameAlreadyTaken,
)
from app.schemas.user import (
    UserUpdate,
)
from app.services.user_service import (
    UserService,
)


@pytest.fixture
def service(
    uow,
):
    return UserService(
        uow,
    )


@pytest.mark.asyncio
async def test_update_profile_username_success(
    service,
    uow,
    user,
):
    data = UserUpdate(
        username="new_username",
    )

    uow.users.get_by_username.return_value = None
    uow.users.update.return_value = user

    result = await service.update_profile(
        user,
        data,
    )

    assert result is user

    assert user.username == (
        "new_username"
    )

    uow.users.get_by_username.assert_awaited_once_with(
        "new_username",
    )

    uow.users.update.assert_awaited_once_with(
        user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_email_success(
    service,
    uow,
    user,
):
    data = UserUpdate(
        email="new@example.com",
    )

    uow.users.get_by_email.return_value = None
    uow.users.update.return_value = user

    result = await service.update_profile(
        user,
        data,
    )

    assert result is user

    assert user.email == (
        "new@example.com"
    )

    uow.users.get_by_email.assert_awaited_once_with(
        "new@example.com",
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_both_fields_success(
    service,
    uow,
    user,
):
    data = UserUpdate(
        username="new_username",
        email="new@example.com",
    )

    uow.users.get_by_username.return_value = None
    uow.users.get_by_email.return_value = None

    uow.users.update.return_value = user

    result = await service.update_profile(
        user,
        data,
    )

    assert result is user

    assert user.username == (
        "new_username"
    )

    assert user.email == (
        "new@example.com"
    )

    uow.users.update.assert_awaited_once_with(
        user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_empty_data(
    service,
    uow,
    user,
):
    uow.users.update.return_value = user

    result = await service.update_profile(
        user,
        UserUpdate(),
    )

    assert result is user

    uow.users.update.assert_awaited_once_with(
        user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_profile_same_username_does_not_check_repository(
    service,
    uow,
    user,
):
    data = UserUpdate(
        username=user.username,
    )

    await service.update_profile(
        user,
        data,
    )

    uow.users.get_by_username.assert_not_called()

    uow.users.update.assert_awaited_once_with(
        user,
    )


@pytest.mark.asyncio
async def test_update_profile_username_conflict(
    service,
    uow,
    user,
):
    data = UserUpdate(
        username="taken",
    )

    uow.users.get_by_username.return_value = (
        object()
    )

    with pytest.raises(
        UsernameAlreadyTaken,
    ):
        await service.update_profile(
            user,
            data,
        )

    uow.users.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_profile_email_conflict(
    service,
    uow,
    user,
):
    data = UserUpdate(
        email="taken@example.com",
    )

    uow.users.get_by_email.return_value = (
        object()
    )

    with pytest.raises(
        EmailAlreadyRegistered,
    ):
        await service.update_profile(
            user,
            data,
        )

    uow.users.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_change_password_success(
    service,
    uow,
    user,
):
    old_version = (
        user.token_version
    )

    with (
        patch(
            "app.services.user_service.verify_password",
            return_value=True,
        ),
        patch(
            "app.services.user_service.hash_password",
            return_value="new-hash",
        ),
    ):
        await service.change_password(
            user,
            "old-password",
            "new-password",
        )

    assert user.hashed_password == (
        "new-hash"
    )

    assert user.token_version == (
        old_version + 1
    )

    uow.users.update.assert_awaited_once_with(
        user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_change_password_invalid_old_password(
    service,
    uow,
    user,
):
    old_hash = (
        user.hashed_password
    )

    with patch(
        "app.services.user_service.verify_password",
        return_value=False,
    ):
        with pytest.raises(
            InvalidCredentials,
        ):
            await service.change_password(
                user,
                "wrong",
                "new-password",
            )

    assert user.hashed_password == old_hash

    uow.users.update.assert_not_called()

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_change_password_database_failure(
    service,
    uow,
    user,
):
    uow.users.update.side_effect = RuntimeError(
        "database error",
    )

    with (
        patch(
            "app.services.user_service.verify_password",
            return_value=True,
        ),
        patch(
            "app.services.user_service.hash_password",
            return_value="hash",
        ),
    ):
        with pytest.raises(
            RuntimeError,
        ):
            await service.change_password(
                user,
                "old",
                "new",
            )

    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_deactivate_success(
    service,
    uow,
    user,
):
    old_version = (
        user.token_version
    )

    await service.deactivate(
        user,
    )

    assert user.is_active is False

    assert user.token_version == (
        old_version + 1
    )

    uow.users.update.assert_awaited_once_with(
        user,
    )

    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_deactivate_already_inactive(
    service,
    uow,
    inactive_user,
):
    old_version = (
        inactive_user.token_version
    )

    await service.deactivate(
        inactive_user,
    )

    assert inactive_user.token_version == (
        old_version
    )

    uow.users.update.assert_not_called()

    uow.commit.assert_not_called()