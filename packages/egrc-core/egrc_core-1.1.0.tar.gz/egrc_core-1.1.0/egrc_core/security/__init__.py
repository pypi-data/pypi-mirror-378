"""
Security module for EGRC Platform.

This module provides comprehensive security utilities including encryption,
hashing, JWT handling, input validation, and security middleware.
"""

from .encryption import (
    decrypt_data,
    encrypt_data,
    generate_key,
    generate_salt,
    hash_password,
    verify_password,
)
from .jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_payload,
    refresh_access_token,
    verify_token,
)
from .middleware import (
    CSRFMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    XSSProtectionMiddleware,
)
from .utils import (
    check_password_strength,
    generate_api_key,
    generate_secure_random,
    generate_session_id,
    mask_sensitive_data,
    scan_for_malware,
    validate_file_type,
)
from .validation import (
    sanitize_input,
    validate_email,
    validate_file_upload,
    validate_input,
    validate_password,
    validate_phone,
    validate_url,
)


__all__ = [
    # Encryption
    "encrypt_data",
    "decrypt_data",
    "generate_key",
    "hash_password",
    "verify_password",
    "generate_salt",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "get_token_payload",
    "refresh_access_token",
    # Validation
    "validate_input",
    "sanitize_input",
    "validate_email",
    "validate_password",
    "validate_phone",
    "validate_url",
    "validate_file_upload",
    # Middleware
    "SecurityMiddleware",
    "RateLimitMiddleware",
    "CSRFMiddleware",
    "XSSProtectionMiddleware",
    # Utilities
    "generate_secure_random",
    "generate_api_key",
    "generate_session_id",
    "mask_sensitive_data",
    "check_password_strength",
    "validate_file_type",
    "scan_for_malware",
]
