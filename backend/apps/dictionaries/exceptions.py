class IcdApiError(Exception):
    """Base exception for ICD-API errors."""


class IcdApiTimeoutError(IcdApiError):
    """Request to ICD-API timed out."""


class IcdApiNotFoundError(IcdApiError):
    """Requested resource was not found (404)."""


class IcdApiUnavailableError(IcdApiError):
    """ICD-API is unavailable (connection refused, 5xx)."""
