class VectorStoreError(Exception):
    """
    Base vector store exception.
    """

class VectorSearchError(VectorStoreError):
    """
    Search operation failed.
    """

class VectorInsertError(VectorStoreError):
    """
    Upsert operation failed.
    """

class VectorDeleteError(VectorStoreError):
    """
    Delete operation failed.
    """

class VectorConfigurationError(VectorStoreError):
    """
    Invalid vector database configuration.
    """