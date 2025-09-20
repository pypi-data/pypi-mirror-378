import asyncio
from typing import Any, Coroutine


async def run_limited(semaphore: asyncio.Semaphore | None, coro: Coroutine) -> Any:
    if semaphore is not None:
        async with semaphore:
            return await coro
    return await coro


_SENTINEL = object()


class AsyncDict[K, V]:
    def __init__(self, initial: dict[K, V] | None = None) -> None:
        self._dict: dict[K, V] = dict(initial or {})
        self._lock = asyncio.Lock()

    async def set(self, key: K, value: V) -> None:
        async with self._lock:
            self._dict[key] = value

    async def pop(self, key: K, default: V | None = _SENTINEL) -> V:
        async with self._lock:
            if default is _SENTINEL:
                return self._dict.pop(key)
            return self._dict.pop(key, default)

    async def values(self) -> list[V]:
        async with self._lock:
            return list(self._dict.values())
