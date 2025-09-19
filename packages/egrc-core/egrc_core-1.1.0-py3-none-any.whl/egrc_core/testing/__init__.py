"""
Testing utilities for EGRC Platform.

This module provides comprehensive testing utilities, fixtures, and helpers
for unit testing, integration testing, and end-to-end testing.
"""

from .decorators import (
    skip_if_no_database,
    skip_if_no_redis,
    with_database,
    with_http_mock,
    with_message_queue,
    with_redis,
)
from .fixtures import (
    DatabaseFixture,
    HTTPFixture,
    MessageQueueFixture,
    RedisFixture,
    get_database_fixture,
    get_http_fixture,
    get_message_queue_fixture,
    get_redis_fixture,
)
from .helpers import (
    assert_cache_has_key,
    assert_database_has_record,
    assert_message_published,
    assert_response_error,
    assert_response_ok,
    cleanup_test_data,
    create_test_data,
)
from .mocks import (
    MockDatabase,
    MockHTTPClient,
    MockMessageQueue,
    MockRedis,
    create_mock_request,
    create_mock_tenant,
    create_mock_user,
)
from .utils import (
    create_test_file,
    create_test_tenant,
    create_test_user,
    generate_test_uuid,
    retry_assertion,
    wait_for_condition,
)


__all__ = [
    # Fixtures
    "DatabaseFixture",
    "RedisFixture",
    "HTTPFixture",
    "MessageQueueFixture",
    "get_database_fixture",
    "get_redis_fixture",
    "get_http_fixture",
    "get_message_queue_fixture",
    # Mocks
    "MockDatabase",
    "MockRedis",
    "MockHTTPClient",
    "MockMessageQueue",
    "create_mock_user",
    "create_mock_tenant",
    "create_mock_request",
    # Helpers
    "assert_response_ok",
    "assert_response_error",
    "assert_database_has_record",
    "assert_cache_has_key",
    "assert_message_published",
    "create_test_data",
    "cleanup_test_data",
    # Decorators
    "with_database",
    "with_redis",
    "with_http_mock",
    "with_message_queue",
    "skip_if_no_database",
    "skip_if_no_redis",
    # Utilities
    "generate_test_uuid",
    "create_test_file",
    "create_test_user",
    "create_test_tenant",
    "wait_for_condition",
    "retry_assertion",
]
