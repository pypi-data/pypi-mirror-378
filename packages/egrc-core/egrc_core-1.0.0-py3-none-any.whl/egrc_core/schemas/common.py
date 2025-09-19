"""
Common schemas for EGRC Platform.

This module provides common Pydantic schemas for standard API responses
and common data structures.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field

from .base import BaseRequestSchema, BaseResponseSchema, BaseSchema


class ErrorDetail(BaseSchema):
    """Schema for error details."""

    field: Optional[str] = Field(
        default=None, description="Field that caused the error"
    )
    message: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ErrorResponse(BaseResponseSchema):
    """Schema for error responses."""

    success: bool = Field(default=False, description="Response success status")
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional error details"
    )
    errors: Optional[List[ErrorDetail]] = Field(
        default_factory=list, description="List of validation errors"
    )


class SuccessResponse(BaseResponseSchema):
    """Schema for success responses."""

    success: bool = Field(default=True, description="Response success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    message: str = Field(
        default="Operation completed successfully", description="Success message"
    )


class HealthCheckResponse(BaseSchema):
    """Schema for health check responses."""

    status: str = Field(description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check timestamp"
    )
    version: Optional[str] = Field(default=None, description="Service version")
    uptime: Optional[float] = Field(
        default=None, description="Service uptime in seconds"
    )
    dependencies: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Dependency statuses"
    )


class PaginationInfo(BaseSchema):
    """Schema for pagination information."""

    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total: int = Field(description="Total number of items")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")


class PaginatedResponse(BaseResponseSchema):
    """Schema for paginated responses."""

    data: List[Any] = Field(description="List of items")
    pagination: PaginationInfo = Field(description="Pagination information")


class SortInfo(BaseSchema):
    """Schema for sorting information."""

    field: str = Field(description="Field being sorted")
    direction: str = Field(description="Sort direction (asc or desc)")


class FilterInfo(BaseSchema):
    """Schema for filter information."""

    field: str = Field(description="Field being filtered")
    operator: str = Field(description="Filter operator")
    value: Any = Field(description="Filter value")


class SearchRequest(BaseRequestSchema):
    """Schema for search requests."""

    query: str = Field(description="Search query")
    fields: Optional[List[str]] = Field(default=None, description="Fields to search in")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional filters"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page"
    )
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order")


class SearchResponse(BaseResponseSchema):
    """Schema for search responses."""

    results: List[Any] = Field(description="Search results")
    total: int = Field(description="Total number of results")
    query: str = Field(description="Search query")
    took: Optional[float] = Field(
        default=None, description="Search time in milliseconds"
    )


class BulkOperationRequest(BaseRequestSchema):
    """Schema for bulk operation requests."""

    operation: str = Field(description="Operation type (create, update, delete)")
    items: List[Dict[str, Any]] = Field(description="Items to process")
    batch_size: Optional[int] = Field(
        default=100, ge=1, le=1000, description="Batch size for processing"
    )


class BulkOperationResponse(BaseResponseSchema):
    """Schema for bulk operation responses."""

    processed: int = Field(description="Number of items processed")
    successful: int = Field(description="Number of successful operations")
    failed: int = Field(description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="List of errors"
    )


class ExportRequest(BaseRequestSchema):
    """Schema for export requests."""

    format: str = Field(default="json", description="Export format (json, csv, xlsx)")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Export filters"
    )
    fields: Optional[List[str]] = Field(default=None, description="Fields to export")
    filename: Optional[str] = Field(default=None, description="Export filename")


class ExportResponse(BaseResponseSchema):
    """Schema for export responses."""

    download_url: str = Field(description="Download URL for the exported file")
    filename: str = Field(description="Exported filename")
    format: str = Field(description="Export format")
    size: Optional[int] = Field(default=None, description="File size in bytes")
    expires_at: Optional[datetime] = Field(
        default=None, description="Download URL expiration time"
    )


class ImportRequest(BaseRequestSchema):
    """Schema for import requests."""

    file_url: Optional[str] = Field(
        default=None, description="URL of the file to import"
    )
    file_content: Optional[str] = Field(
        default=None, description="Base64 encoded file content"
    )
    format: str = Field(default="json", description="Import format (json, csv, xlsx)")
    mapping: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Field mapping"
    )
    validate_only: bool = Field(
        default=False, description="Whether to only validate without importing"
    )


class ImportResponse(BaseResponseSchema):
    """Schema for import responses."""

    total_rows: int = Field(description="Total number of rows in the file")
    processed_rows: int = Field(description="Number of rows processed")
    successful_rows: int = Field(description="Number of successful imports")
    failed_rows: int = Field(description="Number of failed imports")
    errors: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="List of import errors"
    )
    warnings: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="List of import warnings"
    )


class NotificationRequest(BaseRequestSchema):
    """Schema for notification requests."""

    type: str = Field(description="Notification type")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    recipients: List[Union[str, UUID]] = Field(description="List of recipients")
    channels: Optional[List[str]] = Field(
        default_factory=list, description="Notification channels"
    )
    priority: str = Field(default="normal", description="Notification priority")
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional notification data"
    )


class NotificationResponse(BaseResponseSchema):
    """Schema for notification responses."""

    notification_id: str = Field(description="Notification identifier")
    sent_count: int = Field(description="Number of notifications sent")
    failed_count: int = Field(description="Number of failed notifications")
    status: str = Field(description="Notification status")
