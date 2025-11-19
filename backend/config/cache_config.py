"""Cache configuration."""

# Cache TTL (Time To Live) in seconds
CACHE_TTL_REALTIME: int = 2 * 60  # 2 minutes
CACHE_TTL_FORECAST: int = 30 * 60  # 30 minutes
CACHE_TTL_RECOMMENDATIONS: int = 60 * 60  # 1 hour

# Cache key prefixes
CACHE_PREFIX_ANALYSIS: str = "analysis:"
CACHE_PREFIX_FORECAST: str = "forecast:"
CACHE_PREFIX_RECOMMENDATIONS: str = "recommendations:"
