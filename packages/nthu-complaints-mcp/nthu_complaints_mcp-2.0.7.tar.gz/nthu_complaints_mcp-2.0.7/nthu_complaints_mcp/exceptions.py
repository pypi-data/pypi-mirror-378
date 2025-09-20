"""
NTHU Complaints MCP Server Exceptions

Custom exception classes for handling various error conditions
in the NTHU complaints system.
"""

import sys
import time
from typing import Dict, Any, Optional
import httpx
from .models import APITestResult


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


class ErrorHandler:
    """Centralized error handling utilities."""

    @staticmethod
    def log_error(operation: str, error: Exception) -> None:
        """Log error with consistent format."""
        print(f"❌ [stderr] {operation} 發生錯誤: {error}", file=sys.stderr)

    @staticmethod
    def log_info(operation: str, message: str = "") -> None:
        """Log info with consistent format."""
        if message:
            print(f"ℹ️ [stderr] {operation}: {message}", file=sys.stderr)
        else:
            print(f"ℹ️ [stderr] {operation}", file=sys.stderr)

    @staticmethod
    def handle_http_error(error: Exception) -> str:
        """Convert HTTP errors to user-friendly messages."""
        if isinstance(error, httpx.TimeoutException):
            return "連接超時，請檢查網路連接"
        elif isinstance(error, httpx.ConnectError):
            return "無法連接到服務器，請檢查網路或服務狀態"
        elif isinstance(error, httpx.HTTPStatusError):
            return f"API 返回錯誤狀態碼: {error.response.status_code}"
        elif isinstance(error, ValidationError):
            return f"輸入驗證失敗: {error.message}"
        else:
            return str(error)

    @staticmethod
    async def safe_api_call(
        operation: str,
        api_func,
        success_message: str,
        fail_message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute API call with standardized error handling."""
        ErrorHandler.log_info(f"開始{operation}")
        start_time = time.time()

        try:
            result = await api_func(**kwargs)
            execution_time = time.time() - start_time

            ErrorHandler.log_info(f"{operation}完成", f"耗時 {execution_time:.2f}s")

            return APITestResult(
                success=True,
                status_code=getattr(result, 'status_code', 200),
                message=success_message,
                data=result,
                execution_time=execution_time,
            ).dict()

        except Exception as e:
            ErrorHandler.log_error(operation, e)

            return APITestResult(
                success=False,
                message=fail_message,
                error=ErrorHandler.handle_http_error(e),
            ).dict()