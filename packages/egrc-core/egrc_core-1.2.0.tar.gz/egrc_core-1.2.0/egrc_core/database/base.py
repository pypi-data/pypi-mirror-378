"""
Abstract CRUD base class for database operations.

This module provides a comprehensive abstract base class for implementing
CRUD operations across all EGRC services with support for:
- Async/await operations
- Pagination and filtering
- Error handling and validation
- Type safety
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions.exceptions import (
    ConflictError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)


# Note: joinedload and selectinload are not used in this file


# Type aliases
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
IDType = Union[int, str]
FilterType = Dict[str, Any]
OrderByType = Union[str, List[str]]
DBSessionType = AsyncSession


# Simple pagination result class
class PaginatedResult(Generic[ModelType]):
    def __init__(self, items: List[ModelType], total: int, page: int, size: int):
        self.items = items
        self.total = total
        self.page = page
        self.size = size


# Simple pagination params class
class PaginationParams:
    def __init__(self, page: int = 1, size: int = 20):
        self.page = page
        self.size = size


# Simple filter builder
class FilterBuilder:
    def __init__(self, model: Type[ModelType], filters: Dict[str, Any]):
        self.model = model
        self.filters = filters

    def build(self) -> List[Any]:
        """Build filter expressions from the filters dict."""
        expressions = []
        for field, value in self.filters.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                if isinstance(value, dict):
                    # Handle complex filters like {"gte": 10, "lte": 20}
                    for op, val in value.items():
                        if op == "eq":
                            expressions.append(column == val)
                        elif op == "ne":
                            expressions.append(column != val)
                        elif op == "gt":
                            expressions.append(column > val)
                        elif op == "gte":
                            expressions.append(column >= val)
                        elif op == "lt":
                            expressions.append(column < val)
                        elif op == "lte":
                            expressions.append(column <= val)
                        elif op == "like":
                            expressions.append(column.like(f"%{val}%"))
                        elif op == "ilike":
                            expressions.append(column.ilike(f"%{val}%"))
                        elif op == "in":
                            expressions.append(column.in_(val))
                        elif op == "not_in":
                            expressions.append(~column.in_(val))
                else:
                    # Simple equality filter
                    expressions.append(column == value)
        return expressions


def parse_filter_dict(model: Type[ModelType], filters: Dict[str, Any]) -> FilterBuilder:
    """Parse filter dictionary and return a FilterBuilder instance."""
    return FilterBuilder(model, filters)


# Simple pagination helper
class PaginationHelper:
    @staticmethod
    async def get_total_count(db: DBSessionType, query: Any) -> int:
        """Get total count for a query."""
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        return result.scalar() or 0

    @staticmethod
    def apply_pagination(query: Any, pagination: PaginationParams) -> Any:
        """Apply pagination to a query."""
        offset = (pagination.page - 1) * pagination.size
        return query.offset(offset).limit(pagination.size)

    @staticmethod
    def create_paginated_result(
        items: List[ModelType], total: int, pagination: PaginationParams
    ) -> PaginatedResult[ModelType]:
        """Create a paginated result."""
        return PaginatedResult(
            items=items, total=total, page=pagination.page, size=pagination.size
        )


logger = logging.getLogger(__name__)


class BaseCRUD(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base class for CRUD operations.

    This class provides a standard interface for database operations
    that can be implemented by all EGRC services.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD instance.

        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    # Create operations
    async def create(
        self, db: DBSessionType, obj_in: CreateSchemaType, **kwargs
    ) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Data to create
            **kwargs: Additional parameters

        Returns:
            Created model instance

        Raises:
            ValidationError: If validation fails
            ConflictError: If duplicate record exists
            DatabaseError: If database operation fails
        """
        try:
            # Convert Pydantic model to dict
            obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in

            # Add any additional fields
            obj_data.update(kwargs)

            # Create model instance
            db_obj = self.model(**obj_data)

            # Add to session
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)

            self.logger.info(
                f"Created {self.model.__name__} with ID: {getattr(db_obj, 'id', 'unknown')}"
            )
            return db_obj

        except IntegrityError as e:
            await db.rollback()
            self.logger.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise ConflictError(
                resource_type=self.model.__name__,
                field="id",  # This could be improved to detect the actual field
                value=obj_data.get("id", "unknown"),
                details={"error": str(e)},
            )
        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError("create", str(e))

    async def create_many(
        self, db: DBSessionType, objs_in: List[CreateSchemaType], **kwargs
    ) -> List[ModelType]:
        """
        Create multiple records.

        Args:
            db: Database session
            objs_in: List of data to create
            **kwargs: Additional parameters

        Returns:
            List of created model instances
        """
        try:
            db_objs = []
            for obj_in in objs_in:
                obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in
                obj_data.update(kwargs)
                db_obj = self.model(**obj_data)
                db_objs.append(db_obj)

            db.add_all(db_objs)
            await db.commit()

            for db_obj in db_objs:
                await db.refresh(db_obj)

            self.logger.info(f"Created {len(db_objs)} {self.model.__name__} records")
            return db_objs

        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error creating multiple {self.model.__name__}: {e}")
            raise DatabaseError("create_many", str(e))

    # Read operations
    async def get(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance or None if not found
        """
        try:
            query = select(self.model).where(self.model.id == id)

            # Handle soft deletes if model has deleted_at field
            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} with ID {id}: {e}")
            raise DatabaseError("get", str(e))

    async def get_or_404(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> ModelType:
        """
        Get a single record by ID or raise 404 error.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        obj = await self.get(db, id, include_deleted)
        if obj is None:
            raise NotFoundError(resource_type=self.model.__name__, identifier=id)
        return obj

    async def get_multi(
        self,
        db: DBSessionType,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[OrderByType] = None,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of filters
            order_by: Field(s) to order by
            include_deleted: Whether to include soft-deleted records

        Returns:
            List of model instances
        """
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                filter_builder = parse_filter_dict(self.model, filters)
                filter_expressions = filter_builder.build()
                if filter_expressions:
                    query = query.where(and_(*filter_expressions))

            # Handle soft deletes
            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            # Apply ordering
            if order_by:
                if isinstance(order_by, str):
                    order_by = [order_by]
                for field in order_by:
                    if field.startswith("-"):
                        # Descending order
                        field_name = field[1:]
                        column = getattr(self.model, field_name)
                        query = query.order_by(column.desc())
                    else:
                        # Ascending order
                        column = getattr(self.model, field)
                        query = query.order_by(column.asc())

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            self.logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise DatabaseError("get_multi", str(e))

    async def get_paginated(
        self,
        db: DBSessionType,
        pagination: PaginationParams,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[OrderByType] = None,
        include_deleted: bool = False,
    ) -> PaginatedResult[ModelType]:
        """
        Get paginated results.

        Args:
            db: Database session
            pagination: Pagination parameters
            filters: Dictionary of filters
            order_by: Field(s) to order by
            include_deleted: Whether to include soft-deleted records

        Returns:
            Paginated result
        """
        try:
            # Build base query
            query = select(self.model)

            # Apply filters
            if filters:
                filter_builder = parse_filter_dict(self.model, filters)
                filter_expressions = filter_builder.build()
                if filter_expressions:
                    query = query.where(and_(*filter_expressions))

            # Handle soft deletes
            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            # Apply ordering
            if order_by:
                if isinstance(order_by, str):
                    order_by = [order_by]
                for field in order_by:
                    if field.startswith("-"):
                        field_name = field[1:]
                        column = getattr(self.model, field_name)
                        query = query.order_by(column.desc())
                    else:
                        column = getattr(self.model, field)
                        query = query.order_by(column.asc())

            # Get total count
            total = await PaginationHelper.get_total_count(db, query)

            # Apply pagination
            paginated_query = PaginationHelper.apply_pagination(query, pagination)

            # Execute query
            result = await db.execute(paginated_query)
            items = result.scalars().all()

            return PaginationHelper.create_paginated_result(items, total, pagination)

        except Exception as e:
            self.logger.error(f"Error getting paginated {self.model.__name__}: {e}")
            raise DatabaseError("get_paginated", str(e))

    async def count(
        self,
        db: DBSessionType,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False,
    ) -> int:
        """
        Count records matching filters.

        Args:
            db: Database session
            filters: Dictionary of filters
            include_deleted: Whether to include soft-deleted records

        Returns:
            Number of matching records
        """
        try:
            query = select(func.count(self.model.id))

            # Apply filters
            if filters:
                filter_builder = parse_filter_dict(self.model, filters)
                filter_expressions = filter_builder.build()
                if filter_expressions:
                    query = query.where(and_(*filter_expressions))

            # Handle soft deletes
            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar() or 0

        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            raise DatabaseError("count", str(e))

    # Update operations
    async def update(
        self,
        db: DBSessionType,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update a record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Update data

        Returns:
            Updated model instance
        """
        try:
            # Convert to dict if Pydantic model
            if hasattr(obj_in, "dict"):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in

            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            # Update timestamp if model has updated_at field
            if hasattr(db_obj, "updated_at"):
                setattr(db_obj, "updated_at", datetime.utcnow())

            await db.commit()
            await db.refresh(db_obj)

            self.logger.info(
                f"Updated {self.model.__name__} with ID: {getattr(db_obj, 'id', 'unknown')}"
            )
            return db_obj

        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error updating {self.model.__name__}: {e}")
            raise DatabaseError("update", str(e))

    async def update_by_id(
        self,
        db: DBSessionType,
        id: IDType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """
        Update a record by ID.

        Args:
            db: Database session
            id: Record ID
            obj_in: Update data

        Returns:
            Updated model instance or None if not found
        """
        db_obj = await self.get(db, id)
        if db_obj:
            return await self.update(db, db_obj, obj_in)
        return None

    # Delete operations
    async def delete(
        self, db: DBSessionType, id: IDType, soft_delete: bool = True
    ) -> Optional[ModelType]:
        """
        Delete a record.

        Args:
            db: Database session
            id: Record ID
            soft_delete: Whether to soft delete (if supported)

        Returns:
            Deleted model instance or None if not found
        """
        try:
            db_obj = await self.get(db, id)
            if not db_obj:
                return None

            if soft_delete and hasattr(db_obj, "deleted_at"):
                # Soft delete
                setattr(db_obj, "deleted_at", datetime.utcnow())
                await db.commit()
                await db.refresh(db_obj)
            else:
                # Hard delete
                await db.delete(db_obj)
                await db.commit()

            self.logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return db_obj

        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__}: {e}")
            raise DatabaseError("delete", str(e))

    async def delete_many(
        self, db: DBSessionType, ids: List[IDType], soft_delete: bool = True
    ) -> int:
        """
        Delete multiple records.

        Args:
            db: Database session
            ids: List of record IDs
            soft_delete: Whether to soft delete (if supported)

        Returns:
            Number of deleted records
        """
        try:
            if soft_delete and hasattr(self.model, "deleted_at"):
                # Soft delete
                query = (
                    update(self.model)
                    .where(self.model.id.in_(ids))
                    .values(deleted_at=datetime.utcnow())
                )
                result = await db.execute(query)
                await db.commit()
                return result.rowcount
            else:
                # Hard delete
                query = delete(self.model).where(self.model.id.in_(ids))
                result = await db.execute(query)
                await db.commit()
                return result.rowcount

        except Exception as e:
            await db.rollback()
            self.logger.error(f"Error deleting multiple {self.model.__name__}: {e}")
            raise DatabaseError("delete_many", str(e))

    # Utility methods
    async def exists(
        self, db: DBSessionType, id: IDType, include_deleted: bool = False
    ) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            id: Record ID
            include_deleted: Whether to include soft-deleted records

        Returns:
            True if record exists, False otherwise
        """
        try:
            query = select(self.model.id).where(self.model.id == id)

            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            self.logger.error(
                f"Error checking existence of {self.model.__name__} with ID {id}: {e}"
            )
            raise DatabaseError("exists", str(e))

    async def get_by_field(
        self,
        db: DBSessionType,
        field_name: str,
        value: Any,
        include_deleted: bool = False,
    ) -> Optional[ModelType]:
        """
        Get a record by a specific field.

        Args:
            db: Database session
            field_name: Name of the field
            value: Value to match
            include_deleted: Whether to include soft-deleted records

        Returns:
            Model instance or None if not found
        """
        try:
            query = select(self.model).where(getattr(self.model, field_name) == value)

            if not include_deleted and hasattr(self.model, "deleted_at"):
                query = query.where(self.model.deleted_at.is_(None))

            result = await db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(
                f"Error getting {self.model.__name__} by {field_name}: {e}"
            )
            raise DatabaseError("get_by_field", str(e))


class CRUDBase(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Concrete implementation of BaseCRUD.

    This class can be used directly or as a base class for service-specific
    CRUD implementations.
    """

    def __init__(self, model: Type[ModelType]):
        super().__init__(model)
