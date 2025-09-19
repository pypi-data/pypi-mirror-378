"""
Pydantic schemas for audit system.

This module defines Pydantic schemas for audit data validation,
serialization, and API request/response handling.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, root_validator, validator

from .models import AuditAction, AuditSeverity, AuditStatus


class AuditActionEnum(str, Enum):
    """Enumeration of audit actions for Pydantic."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SOFT_DELETE = "SOFT_DELETE"
    RESTORE = "RESTORE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PASSWORD_RESET = "PASSWORD_RESET"
    PERMISSION_GRANT = "PERMISSION_GRANT"
    PERMISSION_REVOKE = "PERMISSION_REVOKE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    ROLE_UNASSIGN = "ROLE_UNASSIGN"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SUBMIT = "SUBMIT"
    PUBLISH = "PUBLISH"
    ARCHIVE = "ARCHIVE"
    UNARCHIVE = "UNARCHIVE"
    CUSTOM = "CUSTOM"


class AuditSeverityEnum(str, Enum):
    """Enumeration of audit severity levels for Pydantic."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AuditStatusEnum(str, Enum):
    """Enumeration of audit status for Pydantic."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


# Base schemas
class AuditBaseSchema(BaseModel):
    """Base schema for audit data."""

    entity_name: str = Field(
        ..., max_length=100, description="Name of the entity being audited"
    )
    entity_id: str = Field(
        ..., max_length=100, description="ID of the entity being audited"
    )
    entity_type: Optional[str] = Field(
        None, max_length=50, description="Type/category of the entity"
    )
    action: AuditActionEnum = Field(..., description="Action performed")
    action_category: Optional[str] = Field(
        None, max_length=50, description="Category of the action"
    )

    # User information
    user_id: Optional[str] = Field(
        None, max_length=100, description="ID of the user who performed the action"
    )
    user_name: Optional[str] = Field(
        None, max_length=200, description="Name of the user"
    )
    user_email: Optional[str] = Field(
        None, max_length=255, description="Email of the user"
    )
    session_id: Optional[str] = Field(None, max_length=100, description="Session ID")

    # Request information
    request_id: Optional[str] = Field(
        None, max_length=100, description="Unique request ID"
    )
    correlation_id: Optional[str] = Field(
        None, max_length=100, description="Correlation ID"
    )

    # Change details
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    changed_fields: Optional[List[str]] = Field(
        None, description="List of changed fields"
    )
    change_summary: Optional[str] = Field(None, description="Summary of changes")

    # Context
    tenant_id: Optional[str] = Field(None, max_length=100, description="Tenant ID")
    organization_id: Optional[str] = Field(
        None, max_length=100, description="Organization ID"
    )
    department_id: Optional[str] = Field(
        None, max_length=100, description="Department ID"
    )

    # Technical details
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    endpoint: Optional[str] = Field(None, max_length=500, description="API endpoint")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method")

    # Audit metadata
    severity: AuditSeverityEnum = Field(
        AuditSeverityEnum.LOW, description="Severity level"
    )
    status: AuditStatusEnum = Field(
        AuditStatusEnum.SUCCESS, description="Operation status"
    )
    error_message: Optional[str] = Field(None, description="Error message")
    error_code: Optional[str] = Field(None, max_length=50, description="Error code")

    # Performance metrics
    execution_time_ms: Optional[int] = Field(
        None, ge=0, description="Execution time in milliseconds"
    )
    memory_usage_mb: Optional[int] = Field(None, ge=0, description="Memory usage in MB")

    # Additional metadata
    tags: Optional[Dict[str, Any]] = Field(None, description="Additional tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Custom fields")


class AuditCreateSchema(AuditBaseSchema):
    """Schema for creating audit entries."""

    pass


class AuditUpdateSchema(BaseModel):
    """Schema for updating audit entries."""

    status: Optional[AuditStatusEnum] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: Optional[int] = Field(None, ge=0)
    memory_usage_mb: Optional[int] = Field(None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class AuditResponseSchema(AuditBaseSchema):
    """Schema for audit entry responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditDetailCreateSchema(BaseModel):
    """Schema for creating audit details."""

    detail_type: str = Field(..., max_length=50, description="Type of detail")
    detail_key: Optional[str] = Field(
        None, max_length=100, description="Key or field name"
    )
    detail_value: Optional[Dict[str, Any]] = Field(None, description="Detail value")
    detail_description: Optional[str] = Field(None, description="Description")
    sequence: int = Field(0, ge=0, description="Sequence number")


class AuditDetailResponseSchema(AuditDetailCreateSchema):
    """Schema for audit detail responses."""

    id: UUID
    audit_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditAttachmentCreateSchema(BaseModel):
    """Schema for creating audit attachments."""

    file_name: str = Field(..., max_length=255, description="File name")
    file_path: str = Field(..., max_length=500, description="File path")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    file_type: Optional[str] = Field(None, max_length=100, description="MIME type")
    file_hash: Optional[str] = Field(None, max_length=64, description="File hash")
    attachment_type: str = Field(..., max_length=50, description="Type of attachment")
    description: Optional[str] = Field(None, description="Description")
    is_encrypted: bool = Field(False, description="Whether file is encrypted")
    encryption_key_id: Optional[str] = Field(
        None, max_length=100, description="Encryption key ID"
    )
    expires_at: Optional[datetime] = Field(None, description="Expiration date")


class AuditAttachmentResponseSchema(AuditAttachmentCreateSchema):
    """Schema for audit attachment responses."""

    id: UUID
    audit_log_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditConfigurationCreateSchema(BaseModel):
    """Schema for creating audit configurations."""

    entity_name: Optional[str] = Field(None, max_length=100, description="Entity name")
    action: Optional[str] = Field(None, max_length=50, description="Action name")
    tenant_id: Optional[str] = Field(None, max_length=100, description="Tenant ID")
    is_enabled: bool = Field(True, description="Whether audit logging is enabled")
    log_level: str = Field("INFO", max_length=20, description="Log level")
    capture_old_values: bool = Field(True, description="Whether to capture old values")
    capture_new_values: bool = Field(True, description="Whether to capture new values")
    capture_metadata: bool = Field(True, description="Whether to capture metadata")
    excluded_fields: Optional[List[str]] = Field(None, description="Fields to exclude")
    included_fields: Optional[List[str]] = Field(None, description="Fields to include")
    field_masks: Optional[Dict[str, str]] = Field(None, description="Fields to mask")
    retention_days: Optional[int] = Field(
        None, ge=1, description="Retention period in days"
    )
    archive_after_days: Optional[int] = Field(
        None, ge=1, description="Archive after days"
    )


class AuditConfigurationUpdateSchema(BaseModel):
    """Schema for updating audit configurations."""

    is_enabled: Optional[bool] = None
    log_level: Optional[str] = Field(None, max_length=20)
    capture_old_values: Optional[bool] = None
    capture_new_values: Optional[bool] = None
    capture_metadata: Optional[bool] = None
    excluded_fields: Optional[List[str]] = None
    included_fields: Optional[List[str]] = None
    field_masks: Optional[Dict[str, str]] = None
    retention_days: Optional[int] = Field(None, ge=1)
    archive_after_days: Optional[int] = Field(None, ge=1)


class AuditConfigurationResponseSchema(AuditConfigurationCreateSchema):
    """Schema for audit configuration responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class AuditRetentionPolicyCreateSchema(BaseModel):
    """Schema for creating audit retention policies."""

    policy_name: str = Field(..., max_length=100, description="Policy name")
    entity_name: Optional[str] = Field(None, max_length=100, description="Entity name")
    action: Optional[str] = Field(None, max_length=50, description="Action")
    severity: Optional[AuditSeverityEnum] = Field(None, description="Severity level")
    tenant_id: Optional[str] = Field(None, max_length=100, description="Tenant ID")
    retention_days: int = Field(..., ge=1, description="Retention period in days")
    archive_after_days: Optional[int] = Field(
        None, ge=1, description="Archive after days"
    )
    delete_after_days: Optional[int] = Field(
        None, ge=1, description="Delete after days"
    )
    archive_location: Optional[str] = Field(
        None, max_length=500, description="Archive location"
    )
    archive_format: str = Field("JSON", max_length=20, description="Archive format")
    compression_enabled: bool = Field(True, description="Whether to compress archives")
    is_active: bool = Field(True, description="Whether policy is active")


class AuditRetentionPolicyUpdateSchema(BaseModel):
    """Schema for updating audit retention policies."""

    policy_name: Optional[str] = Field(None, max_length=100)
    retention_days: Optional[int] = Field(None, ge=1)
    archive_after_days: Optional[int] = Field(None, ge=1)
    delete_after_days: Optional[int] = Field(None, ge=1)
    archive_location: Optional[str] = Field(None, max_length=500)
    archive_format: Optional[str] = Field(None, max_length=20)
    compression_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class AuditRetentionPolicyResponseSchema(AuditRetentionPolicyCreateSchema):
    """Schema for audit retention policy responses."""

    id: UUID
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEventCreateSchema(BaseModel):
    """Schema for creating audit events."""

    event_type: str = Field(..., max_length=50, description="Event type")
    event_data: Dict[str, Any] = Field(..., description="Event data")
    event_metadata: Optional[Dict[str, Any]] = Field(None, description="Event metadata")
    priority: int = Field(5, ge=1, le=10, description="Processing priority")
    max_retries: int = Field(3, ge=0, description="Maximum retries")


class AuditEventResponseSchema(AuditEventCreateSchema):
    """Schema for audit event responses."""

    id: UUID
    status: str
    retry_count: int
    created_at: datetime
    processed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Query and filter schemas
class AuditQuerySchema(BaseModel):
    """Schema for audit query parameters."""

    entity_name: Optional[str] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    action: Optional[AuditActionEnum] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    severity: Optional[AuditSeverityEnum] = None
    status: Optional[AuditStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")


class AuditStatsSchema(BaseModel):
    """Schema for audit statistics."""

    total_audits: int
    audits_by_action: Dict[str, int]
    audits_by_entity: Dict[str, int]
    audits_by_user: Dict[str, int]
    audits_by_severity: Dict[str, int]
    audits_by_status: Dict[str, int]
    audits_by_tenant: Dict[str, int]
    audits_by_hour: Dict[str, int]
    audits_by_day: Dict[str, int]
    average_execution_time: Optional[float] = None
    error_rate: Optional[float] = None


class AuditExportSchema(BaseModel):
    """Schema for audit data export."""

    format: str = Field("json", regex="^(json|csv|xlsx)$", description="Export format")
    entity_name: Optional[str] = None
    action: Optional[AuditActionEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_details: bool = Field(False, description="Include audit details")
    include_attachments: bool = Field(False, description="Include attachments")
    fields: Optional[List[str]] = Field(None, description="Specific fields to export")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")


class AuditBulkCreateSchema(BaseModel):
    """Schema for bulk audit creation."""

    audits: List[AuditCreateSchema] = Field(
        ..., min_items=1, max_items=1000, description="List of audits to create"
    )
    batch_id: Optional[str] = Field(
        None, max_length=100, description="Batch identifier"
    )
    correlation_id: Optional[str] = Field(
        None, max_length=100, description="Correlation ID for the batch"
    )


class AuditBulkResponseSchema(BaseModel):
    """Schema for bulk audit response."""

    batch_id: Optional[str] = None
    correlation_id: Optional[str] = None
    total_created: int
    total_failed: int
    created_ids: List[UUID]
    failed_audits: List[Dict[str, Any]]
    processing_time_ms: int


# Validation schemas
class AuditValidationSchema(BaseModel):
    """Schema for audit data validation."""

    entity_name: str = Field(..., min_length=1, max_length=100)
    entity_id: str = Field(..., min_length=1, max_length=100)
    action: AuditActionEnum

    @validator("entity_name")
    def validate_entity_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Entity name cannot be empty")
        return v.strip()

    @validator("entity_id")
    def validate_entity_id(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Entity ID cannot be empty")
        return v.strip()

    @root_validator
    def validate_change_data(cls, values):
        old_values = values.get("old_values")
        new_values = values.get("new_values")
        changed_fields = values.get("changed_fields")

        # If we have change data, validate consistency
        if old_values or new_values:
            if not changed_fields:
                # Auto-generate changed fields if not provided
                if old_values and new_values:
                    changed_fields = list(
                        set(old_values.keys()) | set(new_values.keys())
                    )
                    values["changed_fields"] = changed_fields

        return values


class AuditSearchSchema(BaseModel):
    """Schema for audit search."""

    query: Optional[str] = Field(None, description="Search query")
    entity_name: Optional[str] = None
    action: Optional[AuditActionEnum] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    severity: Optional[AuditSeverityEnum] = None
    status: Optional[AuditStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[Dict[str, Any]] = None

    # Search options
    search_fields: Optional[List[str]] = Field(None, description="Fields to search in")
    fuzzy_search: bool = Field(False, description="Enable fuzzy search")
    case_sensitive: bool = Field(False, description="Case sensitive search")

    # Pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

    # Sorting
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc", regex="^(asc|desc)$")


class AuditAlertSchema(BaseModel):
    """Schema for audit alerts."""

    alert_name: str = Field(..., max_length=100, description="Alert name")
    description: Optional[str] = Field(None, description="Alert description")
    conditions: Dict[str, Any] = Field(..., description="Alert conditions")
    severity: AuditSeverityEnum = Field(
        AuditSeverityEnum.MEDIUM, description="Alert severity"
    )
    is_enabled: bool = Field(True, description="Whether alert is enabled")
    notification_channels: Optional[List[str]] = Field(
        None, description="Notification channels"
    )
    cooldown_minutes: int = Field(60, ge=0, description="Cooldown period in minutes")
    tenant_id: Optional[str] = Field(None, max_length=100, description="Tenant ID")


class AuditAlertResponseSchema(AuditAlertSchema):
    """Schema for audit alert responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    class Config:
        from_attributes = True
