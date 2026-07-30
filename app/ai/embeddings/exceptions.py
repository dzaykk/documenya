class EmbeddingError(Exception):
    """
    Base embedding exception.
    """

class EmbeddingProviderError(EmbeddingError):
    """
    Provider failed during inference.
    """

class EmbeddingTimeoutError(EmbeddingError):
    """
    Provider request timeout.
    """

class EmbeddingConfigurationError(EmbeddingError):
    """
    Invalid embedding configuration.
    """