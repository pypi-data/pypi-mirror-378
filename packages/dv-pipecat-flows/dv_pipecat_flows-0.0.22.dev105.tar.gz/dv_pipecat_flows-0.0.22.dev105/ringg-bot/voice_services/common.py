"""Common telephony utilities and functions shared across providers."""

import json
from typing import Dict, Optional

import redis.asyncio as redis
from loguru import logger
from utils.generate_config import generate_runtime_config_object, RunConfig

# Global variables that will be set from server.py
_redis_client = None
_websocket_connections = {}
_redis_prefix = "pc_"


def set_redis_client(client: redis.Redis):
    """Set the global Redis client."""
    global _redis_client
    _redis_client = client


def get_redis_client() -> redis.Redis:
    """Get the global Redis client."""
    return _redis_client


def set_websocket_connections(connections: Dict):
    """Set the global websocket connections dict."""
    global _websocket_connections
    _websocket_connections = connections


def get_websocket_connections() -> Dict:
    """Get the global websocket connections dict."""
    return _websocket_connections


def get_redis_key(call_id: str) -> str:
    """Generates a prefixed Redis key for a given call ID."""
    return f"{_redis_prefix}{call_id}"


def get_agent_config_redis_key(agent_id: str) -> str:
    """Generates a prefixed Redis key for agent configuration."""
    return f"{_redis_prefix}agent_{agent_id}"


async def get_runtime_config(call_id: str) -> Optional[RunConfig]:
    """Gets call config from Redis. Decodes bytes to string before JSON parsing."""
    if not _redis_client:
        logger.error("Redis client not available")
        return None

    runtime_config_bytes = await _redis_client.get(get_redis_key(call_id))
    runtime_config = (
        json.loads(runtime_config_bytes.decode("utf-8")) if runtime_config_bytes else None
    )
    runtime_config_object = generate_runtime_config_object(runtime_config)
    return runtime_config_object


async def set_runtime_config(call_id: str, runtime_config: Dict):
    """Sets call config in Redis. Encodes JSON string to bytes."""
    if not _redis_client:
        logger.error("Redis client not available")
        return

    await _redis_client.setex(
        get_redis_key(call_id), 60 * 60, json.dumps(runtime_config).encode("utf-8")
    )


async def delete_call_config(call_id: str):
    """Delete call config from Redis (currently disabled with expiry)."""
    return
    # We might not need this as we have an expiry of 1 hour
    # try:
    #     redis_key = get_redis_key(call_id)
    #     if await _redis_client.exists(redis_key):
    #         await _redis_client.delete(redis_key)
    # except Exception as e:
    #     logger.error(f"Error deleting call config for call_id {call_id}: {e}", call_id=call_id)


async def get_agent_config(agent_id: str) -> Optional[Dict]:
    """Gets agent config from Redis cache. Returns None if not found."""
    if not _redis_client:
        logger.error("Redis client not available")
        return None

    agent_config_bytes = await _redis_client.get(get_agent_config_redis_key(agent_id))
    agent_config = json.loads(agent_config_bytes.decode("utf-8")) if agent_config_bytes else None
    return agent_config


async def set_agent_config(agent_id: str, agent_config: Dict, ttl_minutes: int = 30):
    """Sets agent config in Redis with TTL. Default TTL is 30 minutes."""
    if not _redis_client:
        logger.error("Redis client not available")
        return

    ttl_seconds = ttl_minutes * 60
    await _redis_client.setex(
        get_agent_config_redis_key(agent_id), ttl_seconds, json.dumps(agent_config).encode("utf-8")
    )


def replace_template_variables(text: str, variables: Dict[str, str]) -> str:
    """Replace {{key}} patterns in text with values from variables dict."""
    if not text or not variables:
        return text

    result = text
    for key, value in variables.items():
        pattern = f"{{{{{key}}}}}"
        result = result.replace(pattern, str(value))

    return result
