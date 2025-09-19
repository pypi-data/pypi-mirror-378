"""
Messaging module for EGRC Platform.

This module provides message queue integration with RabbitMQ and Kafka
for inter-service communication, event publishing, and async processing.
"""

from .consumer import MessageConsumer, get_consumer
from .decorators import consume_event, publish_event, retry_on_failure
from .kafka_client import KafkaClient, get_kafka_client
from .models import ConsumerConfig, Event, Message, QueueConfig
from .publisher import MessagePublisher, get_publisher
from .rabbitmq_client import RabbitMQClient, get_rabbitmq_client
from .utils import (
    create_message_id,
    deserialize_message,
    serialize_message,
    validate_message_schema,
)


__all__ = [
    # Clients
    "RabbitMQClient",
    "get_rabbitmq_client",
    "KafkaClient",
    "get_kafka_client",
    # Publisher/Consumer
    "MessagePublisher",
    "get_publisher",
    "MessageConsumer",
    "get_consumer",
    # Decorators
    "publish_event",
    "consume_event",
    "retry_on_failure",
    # Models
    "Message",
    "Event",
    "QueueConfig",
    "ConsumerConfig",
    # Utilities
    "serialize_message",
    "deserialize_message",
    "create_message_id",
    "validate_message_schema",
]
