


class ForebitError(Exception):
    """Base exception for Forebit API errors."""

    pass


class ForebitAuthError(ForebitError):
    """Exception raised for authentication errors."""

    pass


class ForebitAPIError(ForebitError):
    """Exception raised for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ForebitValidationError(ForebitError):
    """Exception raised for validation errors."""

    pass
