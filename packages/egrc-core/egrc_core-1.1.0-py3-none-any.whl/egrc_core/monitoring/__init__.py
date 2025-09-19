"""
Monitoring module for EGRC Platform.

This module provides comprehensive monitoring, metrics, health checks,
and observability features for all EGRC services.
"""

from .alerts import AlertChannel, AlertManager, AlertRule, get_alert_manager
from .health_checks import (
    DatabaseHealthCheck,
    ExternalServiceHealthCheck,
    HealthChecker,
    RedisHealthCheck,
    get_health_checker,
)
from .logging import (
    StructuredLogger,
    get_structured_logger,
    log_error,
    log_metrics,
    log_performance,
)
from .metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    Timer,
    get_metrics_collector,
)
from .tracing import (
    TraceCollector,
    add_trace_span,
    end_trace,
    get_trace_collector,
    start_trace,
)


__all__ = [
    # Metrics
    "MetricsCollector",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "get_metrics_collector",
    # Health Checks
    "HealthChecker",
    "DatabaseHealthCheck",
    "RedisHealthCheck",
    "ExternalServiceHealthCheck",
    "get_health_checker",
    # Tracing
    "TraceCollector",
    "start_trace",
    "end_trace",
    "add_trace_span",
    "get_trace_collector",
    # Logging
    "StructuredLogger",
    "get_structured_logger",
    "log_metrics",
    "log_performance",
    "log_error",
    # Alerts
    "AlertManager",
    "AlertRule",
    "AlertChannel",
    "get_alert_manager",
]
