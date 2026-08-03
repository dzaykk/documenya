import asyncio
import logging

from app.ai.chunking.service import ChunkingService
from app.ai.chunking.splitter import RecursiveTextSplitter
from app.ai.embeddings.providers.factory import (
    EmbeddingProviderFactory,
)
from app.ai.embeddings.service import (
    EmbeddingService,
)
from app.ai.services.document_embedding_service import (
    DocumentEmbeddingService,
)
from app.ai.vectorstores.qdrant.client import (
    ensure_collection_exists,
    get_qdrant_client,
)
from app.ai.vectorstores.qdrant.repository import (
    QdrantVectorStore,
)
from app.ai.vectorstores.service import (
    VectorStoreService,
)
from app.db.session import AsyncWorkerSessionLocal
from app.services.document_parser_service import (
    DocumentParserService,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.uow.sqlalchemy import (
    SQLAlchemyUnitOfWork,
)
from app.workers.celery_app import (
    celery_app,
)

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def process_document_task(
    self,
    document_id: int,
) -> None:

    logger.info(
        "Celery task started for document %s",
        document_id,
    )

    try:

        asyncio.run(
            _process_document(
                document_id,
            )
        )

        logger.info(
            "Celery task finished for document %s",
            document_id,
        )

    except Exception as exc:

        logger.exception(
            "Celery task failed for document %s",
            document_id,
        )

        raise exc


async def _process_document(
    document_id: int,
) -> None:

    logger.info(
        "Creating processing context for document %s",
        document_id,
    )

    async with get_qdrant_client() as client:

        await ensure_collection_exists(
            client,
        )

        logger.info(
            "Qdrant collection ready: %s",
            "documents",
        )

        qdrant_repository = QdrantVectorStore(
            client,
        )

        vector_store = VectorStoreService(
            repository=qdrant_repository,
        )

        embedding_provider = EmbeddingProviderFactory.create()

        embedding_service = EmbeddingService(
            embedding_provider,
        )

        chunking_service = ChunkingService(
            splitter=RecursiveTextSplitter(),
        )

        async with AsyncWorkerSessionLocal() as session:

            uow = SQLAlchemyUnitOfWork(
                session,
            )

            document_embedding_service = DocumentEmbeddingService(
                uow=uow,
                chunking=chunking_service,
                embeddings=embedding_service,
                vector_store=vector_store,
            )

            parser = DocumentParserService()

            service = DocumentProcessingService(
                uow=uow,
                parser=parser,
                document_embedding_service=document_embedding_service,
            )

            await service.process_document(
                document_id,
            )

    logger.info(
        "Processing context closed for document %s",
        document_id,
    )