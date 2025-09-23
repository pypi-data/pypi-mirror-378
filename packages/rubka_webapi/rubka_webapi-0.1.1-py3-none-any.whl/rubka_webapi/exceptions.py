class RubkaWebAPIException(Exception):
    """Base exception for rubka_webapi errors."""
    pass

class NetworkError(RubkaWebAPIException):
    """Raised when a network-related error occurs."""
    pass

class AuthError(RubkaWebAPIException):
    """Raised when authentication fails."""
    pass

class APIError(RubkaWebAPIException):
    """Raised when the Rubika API returns an error."""
    def __init__(self, message: str, code: int = None):
        super().__init__(message)
        self.code = code

class InvalidSessionError(RubkaWebAPIException):
    """Raised when the session data is invalid or expired."""
    pass

