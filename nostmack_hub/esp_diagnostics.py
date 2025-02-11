import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager


@asynccontextmanager
async def start(*, time_between_prints):
    async with asyncio.TaskGroup() as tg:
        diagnostics = EspDiagnostics()
        task = tg.create_task(diagnostics.print_diagnostics_task(time_between_prints))
        try:
            yield diagnostics
        finally:
            task.cancel()


class EspDiagnostics:
    def __init__(self):
        self._seen = {}

    def seen(self, esp_id: int):
        self._seen[esp_id] = self._seen.get(esp_id, 0) + 1

    async def print_diagnostics_task(self, wait):
        while True:
            await asyncio.sleep(wait)
            print(f"Seen esps: {self._diagnostic_message()}")
            self._clear()

    def _clear(self):
        for key in self._seen.keys():
            self._seen[key] = 0

    def _diagnostic_message(self):
        seen = list(self._seen.items())
        seen.sort(key=lambda kv: kv[0])
        return ", ".join(f"{esp_id}: {count}" for esp_id, count in seen)
