import asyncio
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path

import pygame.mixer
from pygame.mixer import Sound

from nostmack_hub import esp_connection_restarter, esp_diagnostics, esp_listener
from nostmack_hub.cancel_on_signal import cancel_on_signal
from nostmack_hub.led_effect import GammaCorrection, SectoredEffect
from nostmack_hub.gear import Gear
from nostmack_hub.machine import Machine
from nostmack_hub.sounds import Sounds
from nostmack_hub.wled import Wled


def checked_getenv(var):
    import os

    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return value


# example: lights.local
WLED_ADDRESS = checked_getenv("WLED_ADDRESS")
LED_COUNT = int(checked_getenv("LED_COUNT"))
GEARS = checked_getenv("GEARS")

SOUND_POOL = Path(checked_getenv("SOUND_POOL"))
SOUND_DING = Path(checked_getenv("SOUND_DING"))
SOUND_FINALE = Path(checked_getenv("SOUND_FINALE"))


async def main():
    with init_pygame_mixer():
        COLOURS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
        esp_mapping = parse_gears(GEARS)
        sounds = list(map(Sound, SOUND_POOL.iterdir()))
        sounds = Sounds(
            gears=list(esp_mapping.values()),
            sounds=sounds,
            ding=Sound(SOUND_DING),
        )
        machine = Machine(
            esp_mapping=esp_mapping,
            esp_events=listen_to_esps(list(esp_mapping.keys())),
            wled=Wled(WLED_ADDRESS),
            effect=GammaCorrection(
                SectoredEffect(COLOURS[: len(esp_mapping)], LED_COUNT)
            ),
            sounds=sounds,
            finale=Sound(SOUND_FINALE),
        )

        await machine.run()


async def listen_to_esps(esp_ids: list[int]):
    async with (
        esp_diagnostics.start(time_between_prints=1) as diagnostics,
        esp_connection_restarter.start(
            esp_ids, timeout=timedelta(minutes=3), restart_fn=shutdown
        ) as restarter,
    ):
        async for id, count in esp_listener.listen_to_esps():
            diagnostics.seen(id)
            restarter.seen(id)

            yield id, count


async def shutdown():
    await asyncio.create_subprocess_exec("systemctl", "reboot")


@contextmanager
def init_pygame_mixer():
    pygame.mixer.init()
    try:
        yield
    finally:
        pygame.mixer.quit()


def parse_gears(gears):
    def parse_gear(gear):
        esp_id, sensitivity = gear.split(":")
        return int(esp_id), Gear(int(sensitivity))

    return dict(map(parse_gear, gears.split(",")))


if __name__ == "__main__":
    asyncio.run(cancel_on_signal(main()))
