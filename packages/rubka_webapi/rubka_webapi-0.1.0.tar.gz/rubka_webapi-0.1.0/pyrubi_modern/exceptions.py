class PyrubiException(Exception):
    """Base exception for pyrubi_modern errors."""
    pass

class NetworkError(PyrubiException):
    """Raised when a network-related error occurs."""
    pass

class AuthError(PyrubiException):
    """Raised when authentication fails."""
    pass

class APIError(PyrubiException):
    """Raised when the Rubika API returns an error."""
    def __init__(self, message: str, code: int = None):
        super().__init__(message)
        self.code = code

class InvalidSessionError(PyrubiException):
    """Raised when the session data is invalid or expired."""
    pass

