class GenAIException(Exception):
    """Base exception for application GenAI integration."""


class GenAIRateLimitError(GenAIException):
    """Exception raised when API limit or resource exhaustion (429) occurs."""


class GenAIAuthError(GenAIException):
    """Exception raised when API key or credentials authentication fails."""
