import asyncio
import functools
from datetime import datetime
from typing import Any, Callable


class AsyncCache:
    def __init__(self, ttl: int) -> None:
        self.ttl = ttl
        self._cache: dict[str, tuple[datetime, Any]] = {}
        self._lock = asyncio.Lock()

    def cache(self, ttl: int | None = None) -> Callable[..., Any]:
        ttl = ttl or self.ttl

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                async with self._lock:
                    key = f'{func.__module__}.{func.__name__}'
                    if key in self._cache:
                        cached_on, result = self._cache[key]
                        if (datetime.utcnow() - cached_on).seconds < ttl:
                            return result

                    result = await func(*args, **kwargs)
                    cached_on = datetime.utcnow()
                    self._cache[key] = (cached_on, result)
                    return result

            return wrapper

        return decorator

    async def purge(self) -> None:
        async with self._lock:
            self._cache = {}


cache = AsyncCache(60)
