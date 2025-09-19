"""
Example implementation of CRUD operations.

This module demonstrates how to use the BaseCRUD class to implement
CRUD operations for a specific model.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from .base import CRUDBase
from .exceptions import NotFoundError, ValidationError
from .pagination import PaginatedResult, PaginationParams
from .types import CreateSchemaType, ModelType, UpdateSchemaType


# Example Pydantic schemas
class UserCreate(BaseModel):
    """Schema for creating a user."""

    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    is_active: bool = Field(default=True, description="Whether user is active")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[str] = Field(None, description="User email address")
    username: Optional[str] = Field(None, description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: Optional[bool] = Field(None, description="Whether user is active")


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Example SQLAlchemy model (this would be in your models module)
class User:
    """Example User model."""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.email = kwargs.get("email")
        self.username = kwargs.get("username")
        self.full_name = kwargs.get("full_name")
        self.is_active = kwargs.get("is_active", True)
        self.created_at = kwargs.get("created_at", datetime.utcnow())
        self.updated_at = kwargs.get("updated_at", datetime.utcnow())
        self.deleted_at = kwargs.get("deleted_at")


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.

    This class extends the base CRUD functionality with
    user-specific operations.
    """

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self.get_by_field(db, "email", email)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.get_by_field(db, "username", username)

    async def get_active_users(
        self, db: AsyncSession, pagination: PaginationParams
    ) -> PaginatedResult[User]:
        """Get all active users with pagination."""
        filters = {"is_active": True}
        return await self.get_paginated(
            db, pagination, filters=filters, order_by=["created_at"]
        )

    async def search_users(
        self, db: AsyncSession, query: str, pagination: PaginationParams
    ) -> PaginatedResult[User]:
        """Search users by name or email."""
        filters = {"full_name__ilike": f"%{query}%", "email__ilike": f"%{query}%"}
        return await self.get_paginated(db, pagination, filters=filters)

    async def activate_user(self, db: AsyncSession, user_id: int) -> User:
        """Activate a user."""
        user = await self.get_or_404(db, user_id)
        return await self.update(db, user, {"is_active": True})

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> User:
        """Deactivate a user."""
        user = await self.get_or_404(db, user_id)
        return await self.update(db, user, {"is_active": False})

    async def get_user_stats(self, db: AsyncSession) -> Dict[str, int]:
        """Get user statistics."""
        total_users = await self.count(db)
        active_users = await self.count(db, filters={"is_active": True})
        inactive_users = total_users - active_users

        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
        }


# Create CRUD instance
user_crud = UserCRUD(User)


# Example usage functions
async def create_user_example(db: AsyncSession):
    """Example of creating a user."""
    user_data = UserCreate(
        email="john.doe@example.com", username="johndoe", full_name="John Doe"
    )

    user = await user_crud.create(db, user_data)
    print(f"Created user: {user.username}")
    return user


async def get_user_example(db: AsyncSession, user_id: int):
    """Example of getting a user."""
    try:
        user = await user_crud.get_or_404(db, user_id)
        print(f"Found user: {user.full_name}")
        return user
    except NotFoundError:
        print(f"User with ID {user_id} not found")
        return None


async def update_user_example(db: AsyncSession, user_id: int):
    """Example of updating a user."""
    update_data = UserUpdate(full_name="John Smith", is_active=False)

    user = await user_crud.update_by_id(db, user_id, update_data)
    if user:
        print(f"Updated user: {user.full_name}")
    return user


async def get_paginated_users_example(db: AsyncSession):
    """Example of getting paginated users."""
    pagination = PaginationParams(page=1, page_size=10)

    result = await user_crud.get_paginated(db, pagination, order_by=["-created_at"])

    print(f"Found {result.total} users")
    print(f"Page {result.page} of {result.pages}")

    for user in result.items:
        print(f"- {user.full_name} ({user.email})")

    return result


async def search_users_example(db: AsyncSession, search_term: str):
    """Example of searching users."""
    pagination = PaginationParams(page=1, page_size=20)

    result = await user_crud.search_users(db, search_term, pagination)

    print(f"Found {result.total} users matching '{search_term}'")

    for user in result.items:
        print(f"- {user.full_name} ({user.email})")

    return result


async def delete_user_example(db: AsyncSession, user_id: int):
    """Example of deleting a user."""
    user = await user_crud.delete(db, user_id, soft_delete=True)
    if user:
        print(f"Deleted user: {user.username}")
    return user


async def get_user_stats_example(db: AsyncSession):
    """Example of getting user statistics."""
    stats = await user_crud.get_user_stats(db)

    print("User Statistics:")
    print(f"- Total users: {stats['total_users']}")
    print(f"- Active users: {stats['active_users']}")
    print(f"- Inactive users: {stats['inactive_users']}")

    return stats


# Example of using filters
async def filter_users_example(db: AsyncSession):
    """Example of filtering users."""
    # Get active users created in the last 30 days
    filters = {
        "is_active": True,
        "created_at__gte": datetime.utcnow().replace(day=1),  # This month
    }

    users = await user_crud.get_multi(
        db, skip=0, limit=50, filters=filters, order_by=["-created_at"]
    )

    print(f"Found {len(users)} active users created this month")

    for user in users:
        print(f"- {user.full_name} (created: {user.created_at})")

    return users


# Example of error handling
async def error_handling_example(db: AsyncSession):
    """Example of proper error handling."""
    try:
        # Try to get a non-existent user
        user = await user_crud.get_or_404(db, 99999)
    except NotFoundError as e:
        print(f"User not found: {e.message}")

    try:
        # Try to create a user with duplicate email
        user_data = UserCreate(
            email="duplicate@example.com",
            username="duplicate",
            full_name="Duplicate User",
        )
        user = await user_crud.create(db, user_data)
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Field errors: {e.field_errors}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # This would be used in your FastAPI application
    print("CRUD Example Implementation")
    print("This module demonstrates how to use the BaseCRUD class")
    print("for implementing CRUD operations in your services.")
