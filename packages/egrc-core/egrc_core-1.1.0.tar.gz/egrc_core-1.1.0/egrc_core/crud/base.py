"""
Abstract base classes for CRUD operations.

This module provides abstract base classes that define the standard
CRUD interface for all EGRC services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..database.base import BaseModel as SQLAlchemyBaseModel
from ..exceptions.exceptions import NotFoundError, ValidationError
from .filters import FilterBuilder
from .pagination import PaginatedResult, PaginationParams
from .sorting import SortParams


# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseCRUD(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base class for CRUD operations.

    This class defines the standard interface for CRUD operations
    that all EGRC services should implement.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD operations for a model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model
        self.filter_builder = FilterBuilder()

    @abstractmethod
    def create(
        self, db: Union[Session, AsyncSession], obj_in: CreateSchemaType, **kwargs: Any
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Data to create
            **kwargs: Additional parameters

        Returns:
            Created model instance
        """
        pass

    @abstractmethod
    def get(
        self, db: Union[Session, AsyncSession], id: Union[int, str, UUID], **kwargs: Any
    ) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Model instance or None
        """
        pass

    @abstractmethod
    def get_multi(
        self,
        db: Union[Session, AsyncSession],
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of model instances
        """
        pass

    @abstractmethod
    def update(
        self,
        db: Union[Session, AsyncSession],
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        **kwargs: Any,
    ) -> ModelType:
        """
        Update a record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Data to update
            **kwargs: Additional parameters

        Returns:
            Updated model instance
        """
        pass

    @abstractmethod
    def delete(
        self, db: Union[Session, AsyncSession], id: Union[int, str, UUID], **kwargs: Any
    ) -> ModelType:
        """
        Delete a record.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Deleted model instance
        """
        pass

    def get_or_404(
        self, db: Union[Session, AsyncSession], id: Union[int, str, UUID], **kwargs: Any
    ) -> ModelType:
        """
        Get a record by ID or raise 404 error.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        obj = self.get(db, id, **kwargs)
        if obj is None:
            raise NotFoundError(resource=self.model.__name__, identifier=str(id))
        return obj

    def exists(
        self, db: Union[Session, AsyncSession], id: Union[int, str, UUID], **kwargs: Any
    ) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            id: Record ID
            **kwargs: Additional parameters

        Returns:
            True if record exists, False otherwise
        """
        return self.get(db, id, **kwargs) is not None

    def count(self, db: Union[Session, AsyncSession], **kwargs: Any) -> int:
        """
        Count total number of records.

        Args:
            db: Database session
            **kwargs: Additional parameters

        Returns:
            Total count
        """
        pass

    def search(
        self,
        db: Union[Session, AsyncSession],
        query: str,
        fields: List[str],
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> List[ModelType]:
        """
        Search records by text query.

        Args:
            db: Database session
            query: Search query
            fields: Fields to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
            **kwargs: Additional parameters

        Returns:
            List of matching model instances
        """
        pass


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
