"""
CRUD operations and abstract base classes for EGRC Platform.

This module provides abstract base classes and common CRUD operations
that can be used across all EGRC services and microservices.
"""

from ..database import BaseCRUD, FilterBuilder, PaginatedResult, PaginationParams
from .base import CRUDMixin
from .filters import QueryFilter
from .repository import AsyncRepository, Repository
from .sorting import SortDirection, SortParams


__all__ = [
    "BaseCRUD",
    "CRUDMixin",
    "Repository",
    "AsyncRepository",
    "FilterBuilder",
    "QueryFilter",
    "PaginationParams",
    "PaginatedResult",
    "SortParams",
    "SortDirection",
]
