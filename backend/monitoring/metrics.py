"""Prometheus metrics.

Метрики для мониторинга:
- API запросы
- LLM вызовы
- Кэш hit/miss
- БД запросы
"""

# from typing import Any, Dict  # F401: unused imports

from prometheus_client import Counter, Histogram  # , Gauge  # F401: unused import

# API metrics
request_count = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint"],
)

# LLM metrics
llm_calls = Counter(
    "llm_calls_total",
    "Total LLM calls",
    ["provider", "model"],
)

llm_latency = Histogram(
    "llm_latency_seconds",
    "LLM call latency",
    ["provider", "model"],
)

# Cache metrics
cache_hits = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type"],
)

cache_misses = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type"],
)


class MetricsCollector:
    """Helper for metrics collection."""

    @staticmethod
    def record_request(
        method: str, endpoint: str, status: int, duration: float
    ) -> None:
        """Record API request."""
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def record_llm_call(provider: str, model: str, latency: float) -> None:
        """Record LLM call."""
        llm_calls.labels(provider=provider, model=model).inc()
        llm_latency.labels(provider=provider, model=model).observe(latency)

    @staticmethod
    def record_cache_access(cache_type: str, hit: bool) -> None:
        """Record cache access."""
        if hit:
            cache_hits.labels(cache_type=cache_type).inc()
        else:
            cache_misses.labels(cache_type=cache_type).inc()


metrics_collector = MetricsCollector()
