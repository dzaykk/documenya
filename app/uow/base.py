from abc import ABC, abstractmethod

from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository


class AbstractUnitOfWork(ABC):

    users: UserRepository
    documents: DocumentRepository

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...