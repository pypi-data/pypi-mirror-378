"""
Database module for EGRC Core.

This module provides database-related functionality including models,
base classes, pagination, sorting, and filtering capabilities.
"""

from .base import BaseCRUD
from .database import (
    Base,
    async_engine,
    async_session_factory,
    engine,
    get_async_db_session,
    get_db_session,
)
from .filters import FilterBuilder, FilterField, FilterOperator, parse_filter_dict
from .models import BaseModel
from .pagination import (
    CursorPaginatedResult,
    CursorPaginationParams,
    PaginatedResult,
    PaginationHelper,
    PaginationParams,
)
from .sorting import SortField, SortHelper, SortOrder, SortParams


__all__ = [
    # Database
    "Base",
    "get_db_session",
    "get_async_db_session",
    "async_session_factory",
    "engine",
    "async_engine",
    # Models
    "BaseModel",
    # CRUD
    "BaseCRUD",
    # Pagination
    "PaginationParams",
    "PaginatedResult",
    "PaginationHelper",
    "CursorPaginationParams",
    "CursorPaginatedResult",
    # Sorting
    "SortField",
    "SortOrder",
    "SortParams",
    "SortHelper",
    # Filtering
    "FilterOperator",
    "FilterField",
    "FilterBuilder",
    "parse_filter_dict",
]
