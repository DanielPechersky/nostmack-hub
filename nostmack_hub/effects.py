import asyncio
from typing import Protocol


class Effect(Protocol):
    def get(self) -> int:
        raise NotImplementedError

    def update(self, counts: int):
        raise NotImplementedError

    async def fully_activated(self):
        raise NotImplementedError


class PeakingEffect(Effect):
    def __init__(self, sensitivity, max_value):
        self.value = 0
        self.sensitivity = sensitivity
        self.max_value = max_value

        self.updated_event = asyncio.Event()
        self.fully_activated_event = asyncio.Event()

    def get(self):
        return self.value

    def update(self, counts):
        if counts == 0:
            return

        self.value = min(self.value + abs(counts) * self.sensitivity, self.max_value)

        self._on_update()

    def _on_update(self):
        self.updated_event.set()
        self.updated_event = asyncio.Event()

        if self.is_fully_activated():
            self.fully_activated_event.set()
            self.fully_activated_event = asyncio.Event()

    async def updated(self):
        await self.updated_event.wait()

    def is_fully_activated(self):
        return self.value == self.max_value

    async def fully_activated(self):
        await self.fully_activated_event.wait()

    async def decay_task(self):
        while True:
            if self.value == 0:
                await self.updated()

            async with asyncio.TaskGroup() as tg:
                update_task = tg.create_task(self.updated())
                try:
                    timeout = 30 if self.is_fully_activated() else 1
                    async with asyncio.timeout(timeout):
                        await asyncio.shield(update_task)
                except asyncio.TimeoutError:
                    while self.value != 0 and not update_task.done():
                        self._decay(self.sensitivity)
                        await asyncio.sleep(0.1)

    def _decay(self, amount):
        self.value = max(0, self.value - amount)
