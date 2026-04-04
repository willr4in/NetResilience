import logging
import redis
from .config import settings

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """
    Возвращает синглтон Redis-клиента.
    Если Redis недоступен — возвращает None (graceful fallback).
    """
    global _client
    if _client is not None:
        return _client
    if not settings.ENABLE_CACHE:
        return None
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        client.ping()
        _client = client
        logger.info("Redis connected: %s", settings.REDIS_URL)
    except Exception as e:
        logger.warning("Redis unavailable, caching disabled: %s", e)
        _client = None
    return _client
