"""
Custom exceptions for the Rose Python SDK.
"""

from typing import Optional, Dict, Any


class RoseAPIError(Exception):
    """Base exception for all Rose API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class RoseAuthenticationError(RoseAPIError):
    """Raised when authentication fails (401)."""

    pass


class RosePermissionError(RoseAPIError):
    """Raised when the user doesn't have permission for the operation (403)."""

    pass


class RoseNotFoundError(RoseAPIError):
    """Raised when a resource is not found (404)."""

    pass


class RoseValidationError(RoseAPIError):
    """Raised when request validation fails (400)."""

    pass


class RoseConflictError(RoseAPIError):
    """Raised when there's a conflict with the current state (409)."""

    pass


class RoseServerError(RoseAPIError):
    """Raised when there's a server error (500)."""

    pass


class RoseTimeoutError(RoseAPIError):
    """Raised when a request times out (504)."""

    pass


class RoseMultiStatusError(RoseAPIError):
    """Raised when some operations succeed and others fail (207)."""

    def __init__(
        self,
        message: str,
        status_code: int = 207,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        failed_records: Optional[list] = None,
    ):
        super().__init__(message, status_code, error_code, details)
        self.failed_records = failed_records or []

    def get_failed_records(self) -> list:
        """Get the list of failed records with their error details."""
        return self.failed_records

    def print_errors(self) -> None:
        """Print detailed error information for failed records."""
        if not self.failed_records:
            print("No detailed error information available.")
            return

        print(f"\n❌ {len(self.failed_records)} record(s) failed:")
        print("=" * 50)

        for i, record_error in enumerate(self.failed_records, 1):
            print(f"\n📋 Failed Record {i}:")
            print(f"   ID: {record_error.get('id', 'Unknown')}")
            print(f"   Data: {record_error.get('data', 'No data')}")
            print(f"   Error: {record_error.get('error', 'Unknown error')}")

            # Try to extract more detailed error information
            error_details = record_error.get("error", {})
            if isinstance(error_details, dict):
                if "message" in error_details:
                    print(f"   Message: {error_details['message']}")
                if "code" in error_details:
                    print(f"   Error Code: {error_details['code']}")
        print()


def raise_for_status(status_code: int, response_data: Dict[str, Any]) -> None:
    """Raise appropriate exception based on HTTP status code."""
    message = response_data.get("message", "Unknown error")
    error = response_data.get("error", "")

    if error:
        message = f"{message}: {error}"

    if status_code == 207:
        # Handle multi-status responses (some records succeeded, some failed)
        failed_records = response_data.get("data", [])
        if not failed_records:
            failed_records = response_data.get("errors", [])

        raise RoseMultiStatusError(
            message="Some records failed to process",
            status_code=status_code,
            details=response_data,
            failed_records=failed_records,
        )
    elif status_code == 400:
        raise RoseValidationError(message, status_code, details=response_data)
    elif status_code == 401:
        raise RoseAuthenticationError(message, status_code, details=response_data)
    elif status_code == 403:
        raise RosePermissionError(message, status_code, details=response_data)
    elif status_code == 404:
        raise RoseNotFoundError(message, status_code, details=response_data)
    elif status_code == 409:
        raise RoseConflictError(message, status_code, details=response_data)
    elif status_code == 500:
        raise RoseServerError(message, status_code, details=response_data)
    elif status_code == 504:
        raise RoseTimeoutError(message, status_code, details=response_data)
    else:
        raise RoseAPIError(message, status_code, details=response_data)
