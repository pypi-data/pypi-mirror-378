import asyncio
from abc import ABC, abstractmethod
from functools import wraps
from logging import Logger
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar

from maestro.core.exceptions import ImproperUsage
from maestro.core.protocols import IO
from maestro.core.type_hints import Seconds

P = ParamSpec("P")
R = TypeVar("R")
RunContext = Callable[[Coroutine[None, None, R]], Coroutine[None, None, R]]


def guard(func: Callable[P, Awaitable[Any]]) -> Callable[P, Awaitable[Any]]:
    @wraps(func)
    async def wrapper(self: "BaseWorker", *args: P.args, **kwargs: P.kwargs) -> Any:
        if self._task is None:
            raise ImproperUsage("Worker is not started yet")
        return await func(self, *args, **kwargs)

    return wrapper


class BaseWorker[I, O](ABC):
    """Базовый класс для всех воркеров"""

    _logger: Logger

    def __init__(
        self,
        name: str,
        input_: IO | None = None,
        output: IO | None = None,
        timeout: Seconds | None = None,
    ):
        self.name = name
        self._input = input_
        self._output = output
        self._task: asyncio.Task | None = None
        self._timeout = timeout

    @property
    def started(self) -> bool:
        return self._task is not None

    @property
    def running(self) -> bool:
        return self.started and not self._task.done()

    @property
    def completed(self) -> bool:
        return self.started and self._task.done()

    async def start(self, run_context: RunContext = lambda x: x) -> asyncio.Task:
        """Основная точка входа."""
        if self._task is None:
            self._task = asyncio.create_task(run_context(self._start()))

        return self._task

    @guard
    async def stop(self) -> None:
        self._task.cancel()

    @guard
    async def wait(
        self, timeout: int | None = None, *, return_exception: bool = False
    ) -> O:
        try:
            return await asyncio.wait_for(self._task, timeout)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            if return_exception:
                return e
            raise e

    async def _start(self) -> None:
        try:
            async with asyncio.timeout(self._timeout):
                await self._run()
        except:
            await self._on_abort()
            raise
        finally:
            await self._on_finish()

    @abstractmethod
    async def _run(self) -> None: ...

    async def _on_abort(self) -> None:
        pass

    async def _on_finish(self) -> None:
        pass

    async def _read_input(self, *, nowait: bool = False) -> I | None:
        if self._input is None:
            return None

        return await self._input.read(nowait=nowait)

    async def _write_output(self, value: O) -> None:
        if self._output is None:
            return None

        return await self._output.write(value)
