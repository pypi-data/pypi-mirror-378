"""
Utilities module for EGRC Core.

This module provides utility functions for data validation,
configuration loading, and common operations.
"""

from .loader import (
    load_config,
    load_database_config,
    load_environment,
    load_logging_config,
    load_secrets,
    load_security_config,
)
from .utils import (
    compress_data,
    convert_timezone,
    decompress_data,
    decrypt_data,
    encrypt_data,
    format_currency,
    format_datetime,
    generate_token,
    generate_uuid,
    get_file_hash,
    hash_password,
    parse_currency,
    parse_datetime,
    sanitize_string,
    validate_email,
    validate_phone,
    validate_url,
    verify_password,
)
from .validation import (
    validate_cache_settings,
    validate_config,
    validate_database_settings,
    validate_email_settings,
    validate_environment,
    validate_security_settings,
)


__all__ = [
    # General Utilities
    "generate_uuid",
    "format_datetime",
    "parse_datetime",
    "validate_email",
    "validate_phone",
    "validate_url",
    "sanitize_string",
    "hash_password",
    "verify_password",
    "generate_token",
    "encrypt_data",
    "decrypt_data",
    "format_currency",
    "parse_currency",
    "convert_timezone",
    "get_file_hash",
    "compress_data",
    "decompress_data",
    # Validation
    "validate_config",
    "validate_environment",
    "validate_security_settings",
    "validate_database_settings",
    "validate_email_settings",
    "validate_cache_settings",
    # Configuration Loading
    "load_config",
    "load_environment",
    "load_secrets",
    "load_database_config",
    "load_security_config",
    "load_logging_config",
]
