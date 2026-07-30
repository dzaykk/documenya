class LLMError(Exception):
    """
    Base LLM exception.
    """

class LLMProviderError(LLMError):
    """
    Provider returned an error.
    """

class LLMTimeoutError(LLMError):
    """
    LLM request timeout.
    """

class LLMConfigurationError(LLMError):
    """
    Invalid provider configuration.
    """

class LLMRateLimitError(LLMError):
    """
    Provider rate limit exceeded.
    """