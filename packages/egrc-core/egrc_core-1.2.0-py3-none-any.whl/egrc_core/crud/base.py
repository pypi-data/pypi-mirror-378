"""
CRUD mixin classes for EGRC Platform.

This module provides mixin classes that can be used to add CRUD functionality
to any class that has access to a database session and model.

Note: BaseCRUD is imported from ..database.base to avoid duplication.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..database import FilterBuilder, PaginatedResult, PaginationParams
from ..database.base import BaseModel as SQLAlchemyBaseModel
from .sorting import SortParams


# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)


class CRUDMixin:
    """
    Mixin class providing common CRUD operations.

    This mixin can be used to add CRUD functionality to any class
    that has access to a database session and model.
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize the mixin with a model."""
        self.model = model
        self.filter_builder = FilterBuilder()

    def _apply_filters(
        self, query: Any, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Apply filters to a query.

        Args:
            query: SQLAlchemy query
            filters: Dictionary of filters

        Returns:
            Filtered query
        """
        if not filters:
            return query

        for field, value in filters.items():
            if hasattr(self.model, field):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model, field).in_(value))
                elif isinstance(value, dict):
                    # Handle range queries
                    if "gte" in value:
                        query = query.filter(getattr(self.model, field) >= value["gte"])
                    if "lte" in value:
                        query = query.filter(getattr(self.model, field) <= value["lte"])
                    if "gt" in value:
                        query = query.filter(getattr(self.model, field) > value["gt"])
                    if "lt" in value:
                        query = query.filter(getattr(self.model, field) < value["lt"])
                    if "like" in value:
                        query = query.filter(
                            getattr(self.model, field).like(f"%{value['like']}%")
                        )
                else:
                    query = query.filter(getattr(self.model, field) == value)

        return query

    def _apply_sorting(
        self, query: Any, sort_params: Optional[SortParams] = None
    ) -> Any:
        """
        Apply sorting to a query.

        Args:
            query: SQLAlchemy query
            sort_params: Sorting parameters

        Returns:
            Sorted query
        """
        if not sort_params:
            return query

        for field, direction in sort_params.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if direction == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        return query

    def _apply_pagination(
        self, query: Any, pagination: Optional[PaginationParams] = None
    ) -> Any:
        """
        Apply pagination to a query.

        Args:
            query: SQLAlchemy query
            pagination: Pagination parameters

        Returns:
            Paginated query
        """
        if not pagination:
            return query

        return query.offset(pagination.skip).limit(pagination.limit)

    def build_query(
        self,
        db: Union[Session, AsyncSession],
        filters: Optional[Dict[str, Any]] = None,
        sort_params: Optional[SortParams] = None,
        pagination: Optional[PaginationParams] = None,
    ) -> Any:
        """
        Build a complete query with filters, sorting, and pagination.

        Args:
            db: Database session
            filters: Dictionary of filters
            sort_params: Sorting parameters
            pagination: Pagination parameters

        Returns:
            Built query
        """
        query = select(self.model)

        # Apply filters
        query = self._apply_filters(query, filters)

        # Apply sorting
        query = self._apply_sorting(query, sort_params)

        # Apply pagination
        query = self._apply_pagination(query, pagination)

        return query

    def get_paginated_result(
        self,
        db: Union[Session, AsyncSession],
        items: List[ModelType],
        total: int,
        pagination: PaginationParams,
    ) -> PaginatedResult[ModelType]:
        """
        Create a paginated result.

        Args:
            db: Database session
            items: List of items
            total: Total count
            pagination: Pagination parameters

        Returns:
            Paginated result
        """
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=(total + pagination.page_size - 1) // pagination.page_size,
        )
