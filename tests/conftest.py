from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from app.models.document import (
    Document,
    DocumentStatus,
)
from app.models.user import User
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)


@pytest.fixture
def uow():
    uow = AsyncMock()

    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None

    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    uow.users = AsyncMock(
        spec=UserRepository,
    )

    uow.documents = AsyncMock(
        spec=DocumentRepository,
    )

    return uow


@pytest.fixture
def storage_service():
    storage = Mock()

    storage.save_file = AsyncMock()
    storage.delete_file = AsyncMock()

    storage.exists = Mock(
        return_value=True,
    )

    return storage


@pytest.fixture
def parser():
    parser = Mock()

    parser.extract_text = AsyncMock()

    return parser


@pytest.fixture
def user():
    user = User(
        email="user@example.com",
        username="John",
        hashed_password="hashed-password",
    )

    user.id = 1
    user.is_active = True
    user.token_version = 1

    return user


@pytest.fixture
def inactive_user():
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password="hashed-password",
    )

    user.id = 2
    user.is_active = False
    user.token_version = 1

    return user


@pytest.fixture
def document(user):
    document = Document(
        owner_id=user.id,
        title="Document",
        filename="file.txt",
        file_path="/tmp/file.txt",
        mime_type="text/plain",
        file_size=123,
    )

    document.id = 1

    document.status = (
        DocumentStatus.PROCESSING.value
    )

    document.processing_error = None
    document.content = None

    document.created_at = datetime.now(
        timezone.utc,
    )

    document.updated_at = datetime.now(
        timezone.utc,
    )

    return document


@pytest.fixture
def upload_file():
    return UploadFile(
        filename="document.txt",
        file=BytesIO(
            b"hello world",
        ),
        headers={
            "content-type": "text/plain",
        },
    )


@pytest.fixture
def query_params():
    return SimpleNamespace(
        search=None,
        page=1,
        limit=20,
    )