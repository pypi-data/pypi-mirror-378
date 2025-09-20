import asyncio
import logging
from functools import partial
from typing import Any, Iterable

from maestro.core.base import BaseWorker
from maestro.group.utils import AsyncDict, run_limited

logger = logging.getLogger(__name__)


class BaseGroupWorker[I, O](BaseWorker[I, O]):
    """
    Базовый класс для группы воркеров. По дефолту список воркеров может быть задан только в момент создании группы,
    однако наследники вправе изменять это поведение.
    """

    def __init__(
        self,
        workers: Iterable[BaseWorker] = (),
        max_concurrency: int | None = None,
        *,
        fail_fast: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._children = AsyncDict[str, BaseWorker](
            {worker.name: worker for worker in workers}
        )
        self._not_spawned_workers = list(workers)
        self._fail_fast = fail_fast

        semaphore = (
            asyncio.Semaphore(max_concurrency)
            if max_concurrency and max_concurrency > 0
            else None
        )
        self._run_context = partial(run_limited, semaphore)

    async def stop(self) -> None:
        await self._stop_children()
        await super().stop()

    async def _stop_children(self) -> None:
        await asyncio.gather(
            *(worker.stop() for worker in await self._workers() if worker.running)
        )

    async def _run(self) -> O:
        await self._spawn_children()

        return_exception = not self._fail_fast
        return await asyncio.gather(
            *(
                worker.wait(return_exception=return_exception)
                for worker in await self._workers()
            ),
            return_exceptions=return_exception,
        )

    async def _spawn_children(self) -> None:
        await asyncio.gather(
            *(self._spawn_child(worker) for worker in self._not_spawned_workers)
        )
        self._not_spawned_workers.clear()

    async def _spawn_child(self, worker: BaseWorker) -> None:
        """Запускает ребёнка в фоне и регистрирует его task."""
        logger.info(f"[BaseGroupWorker] Spawning worker: {worker.name}")
        await worker.start(self._run_context)
        await self._children.set(worker.name, worker)

    async def _collect_finished(self) -> dict[str, Any | Exception]:
        """Забирает результаты завершённых детей, удаляя их."""

        results = {}
        finished_workers = []

        for worker in await self._workers():
            if worker.completed:
                results[worker.name] = await worker.wait(
                    return_exception=not self._fail_fast
                )
                finished_workers.append(worker)

                self._logger.info(
                    f"[{self.__class__.__name__}] Finished worker: {worker.name}, result={results[worker.name]}",
                )

        for worker in finished_workers:
            await self._drop_child(worker)

        return results

    async def _workers(self) -> Iterable[BaseWorker]:
        return await self._children.values()

    async def _drop_child(self, worker: BaseWorker) -> None:
        await self._children.pop(worker.name, None)
        logger.info(f"[BaseGroupWorker] Dropped worker: {worker.name}")
