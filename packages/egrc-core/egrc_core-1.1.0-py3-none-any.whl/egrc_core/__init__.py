"""
EGRC Core - Governance, Risk, and Compliance Platform.

This module provides the core functionality for the EGRC platform including
exceptions, database models, utilities, and comprehensive audit logging.
"""

# Core modules
from . import (
    audit,
    cache,
    config,
    core,
    database,
    graphql,
    http,
    messaging,
    monitoring,
    security,
    storage,
    testing,
    utils,
)

# Version information
from .__version__ import (
    __author__,
    __description__,
    __email__,
    __license__,
    __url__,
    __version__,
    __version_info__,
)
from .audit import (
    AuditContext,
    AuditService,
    audit_hook,
    get_processor_stats,
    get_queue_status,
    log_application_event,
    log_audit,
    log_audit_event,
    log_business_event,
    log_security_event,
    register_model_for_audit,
    setup_audit_middleware,
    start_event_processor,
    stop_event_processor,
    submit_audit_event,
)
from .config import AppConstants, DatabaseConstants, SecurityConstants, Settings

# Re-export commonly used items from core modules
from .core import (
    authenticate_user,
    configure_logging,
    create_access_token,
    get_current_tenant,
    get_current_user,
    get_logger,
)
from .database import (
    Base,
    BaseCRUD,
    BaseModel,
    PaginatedResult,
    PaginationParams,
    get_async_db_session,
    get_db_session,
)

# Exception classes
from .exceptions.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
    ConfigurationError,
    ConflictError,
    DatabaseError,
    EGRCException,
    ExternalServiceError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .utils import (
    format_datetime,
    generate_uuid,
    hash_password,
    validate_email,
    verify_password,
)


__all__ = [
    # Version
    "__version__",
    "__version_info__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
    "__license__",
    # Core modules
    "core",
    "database",
    "config",
    "utils",
    "graphql",
    "audit",
    "cache",
    "messaging",
    "security",
    "monitoring",
    "storage",
    "http",
    "testing",
    # Exceptions
    "EGRCException",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "BusinessLogicError",
    "ExternalServiceError",
    "DatabaseError",
    "RateLimitError",
    "ConfigurationError",
    # Core functionality
    "authenticate_user",
    "create_access_token",
    "get_current_user",
    "get_current_tenant",
    "configure_logging",
    "get_logger",
    # Database
    "Base",
    "get_db_session",
    "get_async_db_session",
    "BaseModel",
    "BaseCRUD",
    "PaginationParams",
    "PaginatedResult",
    # Configuration
    "Settings",
    "AppConstants",
    "DatabaseConstants",
    "SecurityConstants",
    # Utilities
    "generate_uuid",
    "validate_email",
    "hash_password",
    "verify_password",
    "format_datetime",
    # Audit system
    "AuditService",
    "audit_hook",
    "AuditContext",
    "log_audit",
    "log_audit_event",
    "setup_audit_middleware",
    "register_model_for_audit",
    "log_application_event",
    "log_business_event",
    "log_security_event",
    "start_event_processor",
    "stop_event_processor",
    "submit_audit_event",
    "get_processor_stats",
    "get_queue_status",
]
