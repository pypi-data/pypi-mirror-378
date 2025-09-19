"""
Core module for EGRC Core.

This module provides core functionality including authentication,
tenant management, logging, and type definitions.
"""

from .auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    require_permissions,
    verify_token,
)
from .global_id import GlobalID, decode_global_id, encode_global_id, is_global_id
from .logging import Logger, LogLevel, configure_logging, get_logger
from .tenant import TenantContext, TenantManager, get_current_tenant, set_current_tenant
from .types import EmailType, IDType, JSONType, PhoneType, TimestampType, URLType


__all__ = [
    # Authentication
    "authenticate_user",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "require_permissions",
    # Tenant Management
    "get_current_tenant",
    "set_current_tenant",
    "TenantContext",
    "TenantManager",
    # Global ID
    "GlobalID",
    "encode_global_id",
    "decode_global_id",
    "is_global_id",
    # Types
    "IDType",
    "TimestampType",
    "JSONType",
    "EmailType",
    "PhoneType",
    "URLType",
    # Logging
    "configure_logging",
    "get_logger",
    "Logger",
    "LogLevel",
]
