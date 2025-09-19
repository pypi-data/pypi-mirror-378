"""
GraphQL module for EGRC Core.

This module provides GraphQL-related functionality including schemas,
resolvers, and GraphQL API setup.
"""

from .example import ExampleMutation, ExampleQuery, example_schema
from .main import app, create_graphql_app, graphql_app
from .schema import Mutation, Query, Subscription, create_app, create_schema
from .schemas import AuditSchema, BaseSchema, PaginationSchema, TenantSchema, UserSchema


__all__ = [
    # GraphQL Core
    "Query",
    "Mutation",
    "Subscription",
    "create_schema",
    "create_app",
    # Schemas
    "BaseSchema",
    "UserSchema",
    "TenantSchema",
    "AuditSchema",
    "PaginationSchema",
    # FastAPI Integration
    "app",
    "graphql_app",
    "create_graphql_app",
    # Examples
    "ExampleQuery",
    "ExampleMutation",
    "example_schema",
]
