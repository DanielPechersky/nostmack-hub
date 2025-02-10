import asyncio
from contextlib import contextmanager
from pathlib import Path

import pygame.mixer

from nostmack_hub.cancel_on_signal import cancel_on_signal
from nostmack_hub.led_effect import StripedEffect
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


async def main():
    with init_pygame_mixer():
        COLOURS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
        esp_mapping = parse_gears(GEARS)
        sounds = list(map(pygame.mixer.Sound, Path("sounds").iterdir()))
        sounds = Sounds(
            gears=list(esp_mapping.values()),
            sounds=sounds,
        )
        machine = Machine(
            esp_mapping=esp_mapping,
            wled=Wled(WLED_ADDRESS),
            effect=StripedEffect(COLOURS[: len(esp_mapping)], LED_COUNT),
            sounds=sounds,
        )

        await machine.run()


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
