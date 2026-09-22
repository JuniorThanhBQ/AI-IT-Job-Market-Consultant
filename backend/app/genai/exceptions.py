class GenAIException(Exception):
    pass


class GenAIRateLimitError(GenAIException):
    pass


class GenAIAuthError(GenAIException):
    pass
