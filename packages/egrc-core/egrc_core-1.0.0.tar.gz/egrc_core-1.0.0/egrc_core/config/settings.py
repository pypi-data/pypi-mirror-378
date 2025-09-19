"""
Enhanced Configuration management for EGRC Platform.

This module provides centralized configuration management using Pydantic Settings
with environment variable support, constants integration, and comprehensive validation.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..constants.constants import (
    APIResponseMessages,
    AppConstants,
    AuditConstants,
    CacheConstants,
    ComplianceConstants,
    ContentTypes,
    DatabaseConstants,
    DateFormats,
    DefaultValues,
    Environment,
    EnvironmentConstants,
    ErrorCodes,
    FileConstants,
    GraphQLConstants,
    Headers,
    LoggingConstants,
    LogLevel,
    NotificationConstants,
    QueueNames,
    RegexPatterns,
    RetryPolicies,
    SecurityConstants,
    TaskPriorities,
    WorkflowConstants,
)


# from .validation import validate_environment, EnvironmentValidationError
# from .loader import load_configuration


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EGRC_DATABASE_")

    # Database Connection
    url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/egrc_core",
        description="Database connection URL",
    )
    pool_size: int = Field(
        default=DatabaseConstants.DEFAULT_POOL_SIZE, description="Connection pool size"
    )
    max_overflow: int = Field(
        default=DatabaseConstants.DEFAULT_MAX_OVERFLOW,
        description="Max overflow connections",
    )
    pool_timeout: int = Field(
        default=DatabaseConstants.DEFAULT_POOL_TIMEOUT,
        description="Pool timeout in seconds",
    )
    pool_recycle: int = Field(
        default=DatabaseConstants.DEFAULT_POOL_RECYCLE,
        description="Pool recycle time in seconds",
    )
    pool_pre_ping: bool = Field(
        default=DatabaseConstants.DEFAULT_POOL_PRE_PING,
        description="Enable pool pre-ping",
    )
    query_timeout: int = Field(
        default=DatabaseConstants.DEFAULT_QUERY_TIMEOUT,
        description="Query timeout in seconds",
    )
    connection_timeout: int = Field(
        default=DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT,
        description="Connection timeout in seconds",
    )

    # Migration Settings
    migration_dir: str = Field(
        default=DatabaseConstants.MIGRATION_DIR, description="Migration directory"
    )
    migration_script_location: str = Field(
        default=DatabaseConstants.MIGRATION_SCRIPT_LOCATION,
        description="Migration script location",
    )

    @field_validator("pool_size")
    def validate_pool_size(cls, v: int) -> int:
        """Validate pool size."""
        if v < 1 or v > 100:
            raise ValueError("Pool size must be between 1 and 100")
        return v

    @field_validator("max_overflow")
    def validate_max_overflow(cls, v: int) -> int:
        """Validate max overflow."""
        if v < 0 or v > 1000:
            raise ValueError("Max overflow must be between 0 and 1000")
        return v


class CacheSettings(BaseSettings):
    """Cache configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EGRC_CACHE_")

    # Redis Configuration
    redis_url: str = Field(
        default=CacheConstants.REDIS + "://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_pool_size: int = Field(
        default=CacheConstants.DEFAULT_REDIS_POOL_SIZE,
        description="Redis connection pool size",
    )
    redis_timeout: int = Field(
        default=CacheConstants.DEFAULT_REDIS_SOCKET_TIMEOUT,
        description="Redis timeout in seconds",
    )
    redis_retry_on_timeout: bool = Field(
        default=CacheConstants.DEFAULT_REDIS_RETRY_ON_TIMEOUT,
        description="Retry on Redis timeout",
    )

    # Cache Settings
    enabled: bool = Field(default=True, description="Enable caching")
    ttl: int = Field(
        default=CacheConstants.DEFAULT_TTL, description="Default cache TTL in seconds"
    )
    key_prefix: str = Field(
        default=CacheConstants.CACHE_KEY_PREFIX, description="Cache key prefix"
    )

    # Cache Types
    type: str = Field(
        default=CacheConstants.DEFAULT_CACHE_TYPE,
        description="Cache type (redis, memory, file)",
    )

    @field_validator("ttl")
    def validate_ttl(cls, v: int) -> int:
        """Validate cache TTL."""
        if v < 0 or v > 86400:  # Max 24 hours
            raise ValueError("Cache TTL must be between 0 and 86400 seconds")
        return v


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EGRC_SECURITY_")

    # JWT Settings
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this-in-production",
        description="JWT secret key",
    )
    jwt_algorithm: str = Field(
        default=SecurityConstants.DEFAULT_JWT_ALGORITHM, description="JWT algorithm"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=SecurityConstants.DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        description="JWT access token expiration in minutes",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=SecurityConstants.DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        description="JWT refresh token expiration in days",
    )

    # Password Settings
    password_min_length: int = Field(
        default=SecurityConstants.MIN_PASSWORD_LENGTH,
        description="Minimum password length",
    )
    password_max_length: int = Field(
        default=SecurityConstants.MAX_PASSWORD_LENGTH,
        description="Maximum password length",
    )
    password_require_uppercase: bool = Field(
        default=SecurityConstants.PASSWORD_REQUIRE_UPPERCASE,
        description="Require uppercase in password",
    )
    password_require_lowercase: bool = Field(
        default=SecurityConstants.PASSWORD_REQUIRE_LOWERCASE,
        description="Require lowercase in password",
    )
    password_require_numbers: bool = Field(
        default=SecurityConstants.PASSWORD_REQUIRE_NUMBERS,
        description="Require numbers in password",
    )
    password_require_special_chars: bool = Field(
        default=SecurityConstants.PASSWORD_REQUIRE_SPECIAL_CHARS,
        description="Require special characters in password",
    )

    # Encryption Settings
    encryption_key: str = Field(
        default="your-encryption-key-change-this-in-production",
        description="Encryption key",
    )
    encryption_algorithm: str = Field(
        default=SecurityConstants.DEFAULT_ENCRYPTION_ALGORITHM,
        description="Encryption algorithm",
    )
    key_derivation_iterations: int = Field(
        default=SecurityConstants.DEFAULT_KEY_DERIVATION_ITERATIONS,
        description="Key derivation iterations",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=SecurityConstants.DEFAULT_RATE_LIMIT_REQUESTS,
        description="Rate limit requests per window",
    )
    rate_limit_window: int = Field(
        default=SecurityConstants.DEFAULT_RATE_LIMIT_WINDOW,
        description="Rate limit window in seconds",
    )
    rate_limit_burst: int = Field(
        default=SecurityConstants.DEFAULT_RATE_LIMIT_BURST,
        description="Rate limit burst",
    )

    # CORS Settings
    cors_origins: List[str] = Field(
        default=SecurityConstants.DEFAULT_CORS_ORIGINS, description="CORS origins"
    )
    cors_methods: List[str] = Field(
        default=SecurityConstants.DEFAULT_CORS_METHODS, description="CORS methods"
    )
    cors_headers: List[str] = Field(
        default=SecurityConstants.DEFAULT_CORS_HEADERS, description="CORS headers"
    )
    cors_credentials: bool = Field(
        default=SecurityConstants.DEFAULT_CORS_CREDENTIALS,
        description="CORS credentials",
    )

    @field_validator("jwt_secret_key")
    def validate_jwt_secret_key(cls, v: str) -> str:
        """Validate JWT secret key."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    @field_validator("encryption_key")
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key."""
        if len(v) < 32:
            raise ValueError("Encryption key must be at least 32 characters long")
        return v


class KeycloakSettings(BaseSettings):
    """Keycloak configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EGRC_KEYCLOAK_")

    # Keycloak Connection
    url: str = Field(default="http://localhost:8080", description="Keycloak server URL")
    realm: str = Field(default="egrc", description="Keycloak realm name")
    client_id: str = Field(default="egrc-core", description="Keycloak client ID")
    client_secret: str = Field(
        default="your-keycloak-client-secret", description="Keycloak client secret"
    )
    admin_username: str = Field(default="admin", description="Keycloak admin username")
    admin_password: str = Field(default="admin", description="Keycloak admin password")

    # Keycloak Settings
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Retry count for failed requests")

    @property
    def realm_url(self) -> str:
        """Get Keycloak realm URL."""
        return f"{self.url}/realms/{self.realm}"

    @property
    def admin_url(self) -> str:
        """Get Keycloak admin URL."""
        return f"{self.url}/admin/realms/{self.realm}"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    model_config = SettingsConfigDict(env_prefix="EGRC_LOG_")

    # Logging Configuration
    level: str = Field(
        default=LoggingConstants.DEFAULT_LOG_LEVEL, description="Logging level"
    )
    format: str = Field(
        default=LoggingConstants.DEFAULT_LOG_FORMAT,
        description="Log format (json, text, colored)",
    )

    # File Logging
    file_enabled: bool = Field(default=False, description="Enable file logging")
    file_path: Optional[str] = Field(default=None, description="Log file path")
    file_max_size: int = Field(
        default=LoggingConstants.DEFAULT_LOG_FILE_MAX_SIZE,
        description="Max log file size in bytes",
    )
    file_backup_count: int = Field(
        default=LoggingConstants.DEFAULT_LOG_FILE_BACKUP_COUNT,
        description="Number of backup files",
    )
    file_rotation: str = Field(
        default=LoggingConstants.DEFAULT_LOG_FILE_ROTATION,
        description="Log file rotation",
    )

    # Log Fields
    include_timestamp: bool = Field(default=True, description="Include timestamp")
    include_level: bool = Field(default=True, description="Include log level")
    include_module: bool = Field(default=True, description="Include module name")
    include_function: bool = Field(default=True, description="Include function name")
    include_line: bool = Field(default=True, description="Include line number")
    include_request_id: bool = Field(default=True, description="Include request ID")
    include_user_id: bool = Field(default=True, description="Include user ID")
    include_tenant_id: bool = Field(default=True, description="Include tenant ID")

    @field_validator("level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = [
            LoggingConstants.LOG_LEVEL_DEBUG,
            LoggingConstants.LOG_LEVEL_INFO,
            LoggingConstants.LOG_LEVEL_WARNING,
            LoggingConstants.LOG_LEVEL_ERROR,
            LoggingConstants.LOG_LEVEL_CRITICAL,
        ]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()

    @field_validator("format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        allowed_formats = [
            LoggingConstants.LOG_FORMAT_JSON,
            LoggingConstants.LOG_FORMAT_TEXT,
            LoggingConstants.LOG_FORMAT_COLORED,
        ]
        if v.lower() not in allowed_formats:
            raise ValueError(f"Log format must be one of {allowed_formats}")
        return v.lower()


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application Information
    app_name: str = Field(default=AppConstants.APP_NAME, description="Application name")
    app_version: str = Field(
        default=AppConstants.APP_VERSION, description="Application version"
    )
    app_description: str = Field(
        default=AppConstants.APP_DESCRIPTION, description="Application description"
    )
    app_author: str = Field(
        default=AppConstants.APP_AUTHOR, description="Application author"
    )
    app_email: str = Field(
        default=AppConstants.APP_EMAIL, description="Application email"
    )
    app_license: str = Field(
        default=AppConstants.APP_LICENSE, description="Application license"
    )

    # Environment Configuration
    environment: str = Field(
        default=EnvironmentConstants.DEFAULT_ENVIRONMENT,
        description="Environment (development, testing, staging, production, local)",
    )
    debug: bool = Field(default=False, description="Debug mode")
    testing: bool = Field(default=False, description="Testing mode")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of workers")
    reload: bool = Field(default=False, description="Auto-reload on changes")

    # Component Settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    keycloak: KeycloakSettings = Field(default_factory=KeycloakSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @field_validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed_environments = [
            EnvironmentConstants.ENV_DEVELOPMENT,
            EnvironmentConstants.ENV_TESTING,
            EnvironmentConstants.ENV_STAGING,
            EnvironmentConstants.ENV_PRODUCTION,
            EnvironmentConstants.ENV_LOCAL,
        ]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug(cls, v: bool, info) -> bool:
        """Validate debug mode based on environment."""
        # Skip validation if we can't access environment
        try:
            if hasattr(info, 'data') and 'environment' in info.data:
                environment = info.data['environment']
                if environment == EnvironmentConstants.ENV_PRODUCTION and v:
                    raise ValueError("Debug mode cannot be enabled in production")
        except:
            pass  # Skip validation if we can't access the data
        return v

    @model_validator(mode="after")
    def validate_environment_settings(self) -> "Settings":
        """Apply environment-specific settings."""
        environment = self.environment

        if environment in EnvironmentConstants.ENVIRONMENT_SETTINGS:
            env_settings = EnvironmentConstants.ENVIRONMENT_SETTINGS[environment]

            # Apply environment-specific settings
            if "debug" in env_settings:
                self.debug = env_settings["debug"]
            if "log_level" in env_settings:
                self.logging.level = env_settings["log_level"]
            if "reload" in env_settings:
                self.reload = env_settings["reload"]
            if "workers" in env_settings:
                self.workers = env_settings["workers"]

        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == EnvironmentConstants.ENV_DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == EnvironmentConstants.ENV_PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == EnvironmentConstants.ENV_TESTING or self.testing

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.environment == EnvironmentConstants.ENV_STAGING

    @property
    def is_local(self) -> bool:
        """Check if running in local mode."""
        return self.environment == EnvironmentConstants.ENV_LOCAL

    def get_tenant_database_name(self, tenant_name: str, service_name: str) -> str:
        """Get database name for a tenant and service."""
        return f"{tenant_name}_{service_name}"

    def get_tenant_database_url(self, tenant_name: str, service_name: str) -> str:
        """Get database URL for a tenant and service."""
        db_name = self.get_tenant_database_name(tenant_name, service_name)
        base_url = self.database.url.rsplit("/", 1)[0]  # Remove existing database name
        return f"{base_url}/{db_name}"

    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration."""
        return EnvironmentConstants.ENVIRONMENT_SETTINGS.get(
            self.environment,
            EnvironmentConstants.ENVIRONMENT_SETTINGS[
                EnvironmentConstants.DEFAULT_ENVIRONMENT
            ],
        )

    def validate_configuration(self) -> bool:
        """Validate the current configuration."""
        try:
            is_valid, errors, warnings = validate_environment()
            if not is_valid:
                print("Configuration validation failed:")
                for error in errors:
                    print(f"  ❌ {error}")
                for warning in warnings:
                    print(f"  ⚠️  {warning}")
            return is_valid
        except Exception as e:
            print(f"Configuration validation error: {e}")
            return False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
