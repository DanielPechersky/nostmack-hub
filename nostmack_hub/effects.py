import asyncio
from typing import Protocol

from nostmack_hub.saturating_number import SaturatingNumber


class Effect(Protocol):
    def get(self) -> int:
        raise NotImplementedError

    def update(self, counts: int):
        raise NotImplementedError


class PeakingEffect(Effect):
    def __init__(self, sensitivity, max_value: int):
        self.value = SaturatingNumber(0, min=0, max=max_value)
        self.sensitivity = sensitivity

        self.updated_event = asyncio.Event()

    def get(self):
        return self.value.inner

    def update(self, counts):
        if counts == 0:
            return

        self.value.add(abs(counts) * self.sensitivity)

        self._on_update()

    def _on_update(self):
        self.updated_event.set()
        self.updated_event = asyncio.Event()

    async def updated(self):
        await self.updated_event.wait()

    def is_fully_activated(self):
        return self.value.is_max

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
                    while not (self.value.is_min or update_task.done()):
                        self.value.sub(self.sensitivity)
                        await asyncio.sleep(0.1)
