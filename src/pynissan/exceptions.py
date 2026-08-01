from collections.abc import Sequence


class NissanError(Exception):
    """Base exception raised by pynissan."""


class ReadOnlyError(NissanError):
    """Raised when a state-changing operation is blocked by read-only mode."""


class NetworkError(NissanError):
    """Raised when the upstream service cannot be reached."""


class ResponseError(NissanError):
    """Raised when an upstream response has an unexpected shape."""


class AuthenticationError(NissanError):
    """Raised when authentication or token refresh fails."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


class ApiError(NissanError):
    """Raised when the connected vehicle API rejects a request."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


class GraphQLError(NissanError):
    """Raised when a GraphQL response contains operation errors."""

    def __init__(self, messages: Sequence[str]) -> None:
        self.messages = tuple(messages)
        super().__init__("; ".join(self.messages))
