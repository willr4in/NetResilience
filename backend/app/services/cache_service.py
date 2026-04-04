import hashlib
import json
import logging
from typing import Any

from ..cache import get_redis
from ..config import settings

logger = logging.getLogger(__name__)


def _make_hash(data: dict) -> str:
    """SHA256 от детерминированного JSON (ключи отсортированы)."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def make_graph_key(district: str) -> str:
    return f"graph:{district}"


def make_analysis_key(changes: dict) -> str:
    return f"analysis:{changes.get('district', '')}:{_make_hash(changes)}"


def make_cascade_key(request: dict) -> str:
    return f"cascade:{request.get('district', '')}:{_make_hash(request)}"


def get(key: str) -> Any | None:
    """Получить значение из кеша. Возвращает None при промахе или ошибке."""
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning("Cache get error [%s]: %s", key, e)
        return None


def set(key: str, value: Any, ttl: int) -> None:
    """Сохранить значение в кеш с TTL в секундах."""
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logger.warning("Cache set error [%s]: %s", key, e)
