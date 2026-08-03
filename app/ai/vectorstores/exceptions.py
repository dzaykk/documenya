class VectorStoreError(Exception):
    """Base vector store exception."""

class VectorConnectionError(VectorStoreError):
    """Unable to connect to vector database."""

class VectorUpsertError(VectorStoreError):
    """Upsert operation failed."""

class VectorSearchError(VectorStoreError):
    """Search operation failed."""

class VectorDeleteError(VectorStoreError):
    """Delete operation failed."""

class VectorConfigurationError(VectorStoreError):
    """Invalid vector database configuration."""