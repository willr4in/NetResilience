import logging
from typing import Optional

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings

logger = logging.getLogger(__name__)


def _identify(request: Request) -> str:
    """
    Идентификация клиента для rate-limit.
    Авторизованные пользователи лимитируются по access-токену из cookie,
    анонимные — по IP-адресу. Это даёт разные счётчики для разных юзеров
    за одним NAT и единый счётчик для одного юзера с разных вкладок.
    """
    token = request.cookies.get("access_token")
    if token:
        return f"user:{token[-16:]}"
    return get_remote_address(request)


def _build_storage_uri() -> Optional[str]:
    """Если кеш отключён — лимитер работает в in-memory режиме (для тестов и dev без Redis)."""
    if not settings.ENABLE_CACHE:
        return None
    return settings.REDIS_URL


limiter = Limiter(
    key_func=_identify,
    storage_uri=_build_storage_uri() or "memory://",
    strategy="fixed-window",
    default_limits=[],
)
