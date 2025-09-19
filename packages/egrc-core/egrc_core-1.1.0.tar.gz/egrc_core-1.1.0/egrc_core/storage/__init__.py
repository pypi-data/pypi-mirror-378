"""
Storage module for EGRC Platform.

This module provides file handling, storage utilities, and cloud storage
integration for document management and file operations.
"""

from .cloud_storage import (
    AzureBlobStorage,
    GoogleCloudStorage,
    S3Storage,
    get_cloud_storage,
)
from .file_handler import (
    FileDownloader,
    FileHandler,
    FileProcessor,
    FileUploader,
    get_file_handler,
)
from .local_storage import LocalStorage, get_local_storage
from .models import DownloadResult, FileMetadata, StorageConfig, UploadResult
from .utils import (
    compress_file,
    decompress_file,
    extract_metadata,
    generate_file_hash,
    validate_file_size,
    validate_file_type,
)


__all__ = [
    # File Handling
    "FileHandler",
    "FileUploader",
    "FileDownloader",
    "FileProcessor",
    "get_file_handler",
    # Cloud Storage
    "S3Storage",
    "AzureBlobStorage",
    "GoogleCloudStorage",
    "get_cloud_storage",
    # Local Storage
    "LocalStorage",
    "get_local_storage",
    # Models
    "FileMetadata",
    "StorageConfig",
    "UploadResult",
    "DownloadResult",
    # Utilities
    "validate_file_size",
    "validate_file_type",
    "generate_file_hash",
    "compress_file",
    "decompress_file",
    "extract_metadata",
]
