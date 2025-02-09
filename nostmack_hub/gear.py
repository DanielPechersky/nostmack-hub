import asyncio

from nostmack_hub.saturating_number import SaturatingNumber


class Gear:
    def __init__(self, sensitivity) -> None:
        self.value = SaturatingNumber(0, min=0, max=255)
        self.sensitivity = sensitivity
        self._touched_event = asyncio.Event()
        self._charged_event = asyncio.Event()

    def reset(self):
        self.value.inner = 0

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
        self._touched_event.set()
        self._touched_event = asyncio.Event()

    def touched_event(self):
        return self._touched_event

    def _charged(self):
        self._charged_event.set()
        self._charged_event = asyncio.Event()

    def charged_event(self):
        return self._charged_event

    async def _wait_start_discharging(self):
        while True:
            if self.is_discharged():
                await self.touched_event().wait()

            timeout = 30 if self.is_charged() else 1
            try:
                async with asyncio.timeout(timeout):
                    await self.touched_event().wait()
            except asyncio.TimeoutError:
                return

    async def _discharge(self):
        was_touched = self.touched_event()
        while not (self.is_discharged() or was_touched.is_set()):
            self.value.sub(self.sensitivity)
            await asyncio.sleep(0.1)

    async def discharge_task(self):
        while True:
            await self._wait_start_discharging()
            await self._discharge()
