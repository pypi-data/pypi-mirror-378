"""
NTHU Complaints MCP Server Exceptions

Custom exception classes for handling various error conditions
in the NTHU complaints system.
"""


class NTHUComplaintsError(Exception):
    """Base exception class for NTHU complaints system."""

    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code


class APIConnectionError(NTHUComplaintsError):
    """Raised when unable to connect to the NTHU complaints API."""

    def __init__(self, message: str = "Unable to connect to NTHU complaints API"):
        super().__init__(message, "API_CONNECTION_ERROR")


class ValidationError(NTHUComplaintsError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class AuthenticationError(NTHUComplaintsError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class ComplaintNotFoundError(NTHUComplaintsError):
    """Raised when a complaint cannot be found."""

    def __init__(self, case_number: str = None):
        message = f"Complaint not found: {case_number}" if case_number else "Complaint not found"
        super().__init__(message, "COMPLAINT_NOT_FOUND")
        self.case_number = case_number


class RateLimitError(NTHUComplaintsError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR")