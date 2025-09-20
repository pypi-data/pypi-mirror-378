"""
HTTP client utilities for standardized configuration.

This module provides utilities for creating aiohttp ClientSession instances
with standardized configuration from env_config.py.
"""

import aiohttp
from env_config import api_config


def get_plivo_timeout() -> aiohttp.ClientTimeout:
    """
    Get Plivo-specific timeout configuration with longer timeouts for call initiation.

    Returns:
        Configured ClientTimeout instance optimized for Plivo API calls
    """
    return aiohttp.ClientTimeout(
        total=api_config.PLIVO_API_TIMEOUT,
        connect=api_config.HTTP_CLIENT_TIMEOUT_CONNECT,
        sock_read=api_config.PLIVO_API_TIMEOUT - 5.0,  # Slightly less than total
    )


def get_plivo_connector() -> aiohttp.TCPConnector:
    """
    Get Plivo-specific connector configuration with optimized settings for telephony.

    Returns:
        Configured TCPConnector instance optimized for Plivo API calls
    """
    return aiohttp.TCPConnector(
        limit=20,  # Reduced pool for better timeout handling
        limit_per_host=5,  # Conservative per-host limit
        ttl_dns_cache=api_config.HTTP_CLIENT_DNS_CACHE_TTL,
        use_dns_cache=True,
        keepalive_timeout=60,  # Longer keepalive for telephony APIs
        enable_cleanup_closed=True,
    )


def create_http_client_session(**kwargs) -> aiohttp.ClientSession:
    """
    Create an aiohttp ClientSession with standardized configuration.

    Uses configuration values from env_config.py for timeouts, connection pooling,
    and other HTTP client settings. Additional keyword arguments can be passed
    to override defaults or add extra configuration.

    Args:
        **kwargs: Additional keyword arguments to pass to ClientSession constructor.
                 These will override the default configuration values.

    Returns:
        Configured aiohttp ClientSession instance
    """
    # Default timeout configuration
    timeout = aiohttp.ClientTimeout(
        total=api_config.HTTP_CLIENT_TIMEOUT_TOTAL,
        connect=api_config.HTTP_CLIENT_TIMEOUT_CONNECT,
        sock_read=api_config.HTTP_CLIENT_TIMEOUT_READ,
    )

    # Default connector configuration
    connector = aiohttp.TCPConnector(
        limit=api_config.HTTP_CLIENT_POOL_SIZE,
        limit_per_host=api_config.HTTP_CLIENT_POOL_SIZE_PER_HOST,
        ttl_dns_cache=api_config.HTTP_CLIENT_DNS_CACHE_TTL,
        use_dns_cache=True,
        keepalive_timeout=api_config.HTTP_CLIENT_KEEPALIVE_TIMEOUT,
        enable_cleanup_closed=True,
    )

    # Default session configuration
    session_config = {
        "timeout": timeout,
        "connector": connector,
        "raise_for_status": False,  # We'll handle status codes ourselves
    }

    # Override with any provided kwargs
    session_config.update(kwargs)

    return aiohttp.ClientSession(**session_config)


def get_default_timeout() -> aiohttp.ClientTimeout:
    """
    Get the default ClientTimeout configuration.

    Returns:
        Configured ClientTimeout instance
    """
    return aiohttp.ClientTimeout(
        total=api_config.HTTP_CLIENT_TIMEOUT_TOTAL,
        connect=api_config.HTTP_CLIENT_TIMEOUT_CONNECT,
        sock_read=api_config.HTTP_CLIENT_TIMEOUT_READ,
    )


def get_default_connector() -> aiohttp.TCPConnector:
    """
    Get the default TCPConnector configuration.

    Returns:
        Configured TCPConnector instance
    """
    return aiohttp.TCPConnector(
        limit=api_config.HTTP_CLIENT_POOL_SIZE,
        limit_per_host=api_config.HTTP_CLIENT_POOL_SIZE_PER_HOST,
        ttl_dns_cache=api_config.HTTP_CLIENT_DNS_CACHE_TTL,
        use_dns_cache=True,
        keepalive_timeout=api_config.HTTP_CLIENT_KEEPALIVE_TIMEOUT,
        enable_cleanup_closed=True,
    )
