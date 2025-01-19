import asyncio

from nostmack_hub.saturating_number import SaturatingNumber


class Gear:
    def __init__(self, sensitivity, max) -> None:
        self.value = SaturatingNumber(0, min=0, max=max)
        self.sensitivity = sensitivity
        self.touched_event = asyncio.Event()
        self.charged_event = asyncio.Event()

    def turned(self, amount: int):
        if amount == 0:
            return

        self.value.add(abs(amount) * self.sensitivity)
        self._touched()

        if self.is_charged():
            self._charged()

    def is_discharged(self):
        return self.value.is_min

    def is_charged(self):
        return self.value.is_max

    def _touched(self):
        self.touched_event.set()
        self.touched_event = asyncio.Event()

    async def wait_touched(self):
        await self.touched_event.wait()

    def _charged(self):
        self.charged_event.set()
        self.charged_event = asyncio.Event()

    async def wait_charged(self):
        await self.charged_event.wait()

    async def _wait_start_discharging(self):
        while True:
            if self.is_discharged():
                await self.wait_touched()

            timeout = 30 if self.is_charged() else 1
            try:
                async with asyncio.timeout(timeout):
                    await self.wait_touched()
            except asyncio.TimeoutError:
                return

    async def _discharge(self):
        async with asyncio.TaskGroup() as tg:
            touched_task = tg.create_task(self.wait_touched())
            while not (self.is_discharged() or touched_task.done()):
                self.value.sub(self.sensitivity)
                await asyncio.sleep(0.1)
            touched_task.cancel()

    async def discharge_task(self):
        while True:
            await self._wait_start_discharging()
            await self._discharge()
