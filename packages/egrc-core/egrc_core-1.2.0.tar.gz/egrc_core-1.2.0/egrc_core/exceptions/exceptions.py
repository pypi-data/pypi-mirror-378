"""
Custom exceptions for EGRC Platform.

This module defines custom exception classes used throughout the EGRC platform
for better error handling and API responses.
"""

from typing import Any, Dict, Optional


class EGRCException(Exception):
    """Base exception class for EGRC Platform."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ) -> None:
        """Initialize EGRC exception.

        Args:
            message: Error message
            error_code: Unique error code
            details: Additional error details
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code


class ValidationError(EGRCException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional validation details
        """
        error_details = details or {}
        if field is not None:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = value

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=error_details,
            status_code=400,
        )


class NotFoundError(EGRCException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        message: Optional[str] = None,
    ) -> None:
        """Initialize not found error.

        Args:
            resource: Type of resource not found
            identifier: Identifier of the resource
            message: Custom error message
        """
        if message is None:
            message = f"{resource} not found"
            if identifier is not None:
                message += f" with identifier: {identifier}"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
            status_code=404,
        )


class AuthenticationError(EGRCException):
    """Exception raised for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize authentication error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            status_code=401,
        )


class AuthorizationError(EGRCException):
    """Exception raised for authorization errors."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize authorization error.

        Args:
            message: Error message
            resource: Resource that was accessed
            action: Action that was attempted
            details: Additional error details
        """
        error_details = details or {}
        if resource is not None:
            error_details["resource"] = resource
        if action is not None:
            error_details["action"] = action

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=error_details,
            status_code=403,
        )


class ConflictError(EGRCException):
    """Exception raised for resource conflicts."""

    def __init__(
        self,
        message: str = "Resource conflict",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize conflict error.

        Args:
            message: Error message
            resource: Resource that has conflict
            details: Additional error details
        """
        error_details = details or {}
        if resource is not None:
            error_details["resource"] = resource

        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=error_details,
            status_code=409,
        )


class BusinessLogicError(EGRCException):
    """Exception raised for business logic violations."""

    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize business logic error.

        Args:
            message: Error message
            rule: Business rule that was violated
            details: Additional error details
        """
        error_details = details or {}
        if rule is not None:
            error_details["rule"] = rule

        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=error_details,
            status_code=422,
        )


class ExternalServiceError(EGRCException):
    """Exception raised for external service errors."""

    def __init__(
        self,
        service: str,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize external service error.

        Args:
            service: Name of the external service
            message: Error message
            status_code: HTTP status code from external service
            details: Additional error details
        """
        error_details = details or {}
        error_details["service"] = service
        if status_code is not None:
            error_details["external_status_code"] = status_code

        super().__init__(
            message=f"External service error ({service}): {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=error_details,
            status_code=502,
        )


class DatabaseError(EGRCException):
    """Exception raised for database errors."""

    def __init__(
        self,
        message: str = "Database error",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize database error.

        Args:
            message: Error message
            operation: Database operation that failed
            details: Additional error details
        """
        error_details = details or {}
        if operation is not None:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=error_details,
            status_code=500,
        )


class RateLimitError(EGRCException):
    """Exception raised for rate limit violations."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            limit: Rate limit
            window: Time window in seconds
            retry_after: Seconds to wait before retry
        """
        details = {}
        if limit is not None:
            details["limit"] = limit
        if window is not None:
            details["window"] = window
        if retry_after is not None:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=429,
        )


class ConfigurationError(EGRCException):
    """Exception raised for configuration errors."""

    def __init__(
        self,
        message: str = "Configuration error",
        setting: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            setting: Configuration setting that has error
            details: Additional error details
        """
        error_details = details or {}
        if setting is not None:
            error_details["setting"] = setting

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=error_details,
            status_code=500,
        )


class CacheException(EGRCException):
    """Exception raised for cache-related errors."""

    def __init__(
        self,
        message: str = "Cache error",
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize cache exception.

        Args:
            message: Error message
            cache_key: Cache key that caused the error
            operation: Cache operation that failed
            details: Additional error details
        """
        error_details = details or {}
        if cache_key:
            error_details["cache_key"] = cache_key
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=error_details,
            status_code=500,
        )
