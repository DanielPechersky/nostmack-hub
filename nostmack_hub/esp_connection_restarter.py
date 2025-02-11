import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta


@asynccontextmanager
async def start(esp_ids: list[int], timeout: timedelta, restart_fn):
    async with asyncio.TaskGroup() as tg:
        restarter = EspConnectionRestarter(esp_ids)
        task = tg.create_task(restarter.restart_if_esp_missing(timeout, restart_fn))
        try:
            yield restarter
        finally:
            task.cancel()


class EspConnectionRestarter:
    def __init__(self, esp_ids):
        self.last_seen_map = {esp_id: datetime.now() for esp_id in esp_ids}

    def seen(self, esp_id: int):
        if esp_id in self.last_seen_map:
            self.last_seen_map[esp_id] = datetime.now()

    async def restart_if_esp_missing(self, timeout, restart_fn):
        while True:
            await asyncio.sleep(1)
            disconnected_esps = [
                esp_id
                for esp_id, last_seen in self.last_seen_map.items()
                if (datetime.now() - last_seen) > timeout
            ]
            if len(disconnected_esps) > 0:
                print(f"Some ESPs were disconnected for {timeout}: {disconnected_esps}")
                await restart_fn()
