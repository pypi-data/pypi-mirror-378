"""
HTTP client module for EGRC Platform.

This module provides HTTP client utilities for inter-service communication,
API calls, and external service integration.
"""

from .client import AsyncHTTPClient, HTTPClient, get_async_http_client, get_http_client
from .decorators import (
    circuit_breaker,
    rate_limit_request,
    retry_request,
    timeout_request,
)
from .models import (
    CircuitBreakerConfig,
    HTTPConfig,
    HTTPRequest,
    HTTPResponse,
    RetryConfig,
)
from .utils import (
    build_url,
    get_request_headers,
    handle_http_error,
    parse_response,
    validate_ssl_cert,
)


__all__ = [
    # Clients
    "HTTPClient",
    "AsyncHTTPClient",
    "get_http_client",
    "get_async_http_client",
    # Decorators
    "retry_request",
    "circuit_breaker",
    "timeout_request",
    "rate_limit_request",
    # Models
    "HTTPRequest",
    "HTTPResponse",
    "HTTPConfig",
    "RetryConfig",
    "CircuitBreakerConfig",
    # Utilities
    "build_url",
    "parse_response",
    "handle_http_error",
    "validate_ssl_cert",
    "get_request_headers",
]
