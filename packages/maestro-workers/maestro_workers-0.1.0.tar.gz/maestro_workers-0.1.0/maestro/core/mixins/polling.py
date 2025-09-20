import asyncio
import logging
from abc import ABC, abstractmethod

from maestro.core.base import BaseWorker
from maestro.core.type_hints import Seconds


class PollingWorkerMixin[I, O](BaseWorker[I, O], ABC):
    """
    Воркер с заданием, которое имеет смысл перезапускать с некоторым интервалом в течение неопределённого
    периода времени. Всегда завершать вручную.
    """

    def __init__(self, interval: Seconds, *args, **kwargs):
        self._interval = interval
        self._stop_event = asyncio.Event()
        self._logger = logging.getLogger(__name__)
        super().__init__(*args, **kwargs)

    async def stop(self) -> None:
        self._stop_event.set()
        await super().stop()

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self._step()
            except Exception as e:
                self._logger.exception(e)

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

        return None

    @abstractmethod
    async def _step(self) -> None:
        """
        Одна итерация работы воркера.
        """
        ...
