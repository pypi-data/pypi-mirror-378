import asyncio
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Callable, TypeAlias

from maestro.core.base import BaseWorker
from maestro.core.exceptions import IncorrectConfiguring
from maestro.core.mixins.polling import PollingWorkerMixin
from maestro.core.protocols import IO
from maestro.group.base import BaseGroupWorker

Factory: TypeAlias = Callable[[dict], BaseWorker]


class Orchestrator[T](
    PollingWorkerMixin, BaseGroupWorker[dict, dict[str, Any | Exception]], ABC
):
    """Воркер, поддерживающий добавление новых воркеров через input и factory."""

    def __init__(self, input_factory: type[IO], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = getLogger(__name__)
        self._input_factory = input_factory

        if kwargs.get("input_") is None:
            raise IncorrectConfiguring(
                "Orchestrator can't have factory without input queue"
            )

    async def _step(self) -> None:
        await self._spawn_from_input()
        await self._collect_finished()

    async def _spawn_from_input(self) -> None:
        while True:
            instruction = await self._safe_read_from_input()
            if instruction is None:
                break

            input_ = self._input_factory()
            worker = self._factory(input_)

            await input_.write(instruction)
            await self._spawn_child(worker)

    async def _safe_read_from_input(self) -> Any | None:
        try:
            return await self._read_input(nowait=True)
        except asyncio.QueueEmpty:
            return None

    @abstractmethod
    def _factory(self, input_: IO) -> T: ...
