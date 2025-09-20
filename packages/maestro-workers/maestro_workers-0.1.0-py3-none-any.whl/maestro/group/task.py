from functools import cached_property
from logging import Logger, getLogger
from typing import Any

from maestro.group.base import BaseGroupWorker


class Task[I](BaseGroupWorker[I, dict[str, Any]]):
    """
    Воркер, реализующий последовательную работу нескольких воркеров, объединённых в единую задачу.

    Позволяет воркерам выкидывать исключения, но пользоваться этим механизмом нужно только тогда, когда воркеры,
    следующие за текущим не зависят от его результата и не должны сделать что-то в случае его неуспеха.
    """

    @cached_property
    def _logger(self) -> Logger:
        return getLogger(__name__)

    async def _run(self) -> None:
        await self._collect_finished()

    async def _collect_finished(self) -> dict[str, Any]:
        workers_results = {}
        for worker in await self._workers():
            await worker.start()

            try:
                workers_results[worker.name] = await worker.wait(
                    return_exception=not self._fail_fast
                )
            except Exception as e:
                self._logger.error(e)
                raise

        return workers_results
