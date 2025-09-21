class CiderError(Exception):
    pass

class ConnectionError(CiderError):
    pass

class AuthenticationError(CiderError):
    pass

class ValidationError(CiderError):
    pass

class APIServerError(CiderError):
    pass

class NotSupportedError(CiderError):
    pass
