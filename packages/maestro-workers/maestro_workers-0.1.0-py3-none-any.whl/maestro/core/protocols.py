from typing import Protocol


class IO[T](Protocol):
    async def read(self, *, nowait: bool = False) -> T: ...

    async def write(self, value: T) -> None: ...
