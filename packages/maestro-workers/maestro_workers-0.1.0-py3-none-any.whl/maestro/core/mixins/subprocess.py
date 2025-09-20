import asyncio
from abc import ABC

from maestro.core.base import BaseWorker


class SubprocessWorkerMixin[I, O](BaseWorker[I, O], ABC):
    """
    Воркер с заданием, для выполнения которого необходим внешний исполняемый файл.
    """

    @staticmethod
    async def _run_subprocess(
        *args: str,
        input_data: bytes | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
    ) -> tuple[int, str, str]:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=input_data), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise

        return proc.returncode, stdout.decode(), stderr.decode()
