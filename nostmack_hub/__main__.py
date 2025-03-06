import asyncio
from contextlib import contextmanager
from pathlib import Path

import pygame.mixer
from pygame.mixer import Sound

from nostmack_hub import esp_diagnostics, esp_listener, pygame_mixer
from nostmack_hub.cancel_on_signal import cancel_on_signal
from nostmack_hub.led_effect import flowing_memento
from nostmack_hub.gear import Gear
from nostmack_hub.led_effect.gamma_correction import GammaCorrection
from nostmack_hub.led_value_calculator import LedEffectFixedCount
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
COLOURS = checked_getenv("COLOURS")
FINALE_DURATION = int(checked_getenv("FINALE_DURATION"))

SOUND_POOL = Path(checked_getenv("SOUND_POOL"))
SOUND_DING = Path(checked_getenv("SOUND_DING"))
SOUND_FINALE = Path(checked_getenv("SOUND_FINALE"))


async def main():
    with pygame_mixer.init():
        colours = parse_colours(COLOURS)
        esp_mapping = parse_gears(GEARS)
        sounds = list(map(Sound, SOUND_POOL.iterdir()))
        sounds = Sounds(
            gears=list(esp_mapping.values()),
            sounds=sounds,
            ding=Sound(SOUND_DING),
        )
        machine = Machine(
            esp_mapping=esp_mapping,
            esp_events=listen_to_esps(),
            wled=Wled(WLED_ADDRESS),
            effect=LedEffectFixedCount(
                GammaCorrection(
                    flowing_memento.effect(colours, LED_COUNT),
                ),
                LED_COUNT,
            ),
            sounds=sounds,
            finale=Sound(SOUND_FINALE),
            finale_duration=FINALE_DURATION,
        )

        await machine.run()


async def listen_to_esps():
    async with esp_diagnostics.start(time_between_prints=1) as diagnostics:
        async for id, count in esp_listener.listen_to_esps():
            diagnostics.seen(id)

            yield id, count


def parse_gears(gears):
    def parse_gear(gear):
        esp_id, sensitivity = gear.split(":")
        return int(esp_id), Gear(int(sensitivity))

    return dict(map(parse_gear, gears.split(",")))


def parse_colours(colours):
    import json

    colours = json.loads(colours)

    return colours


if __name__ == "__main__":
    asyncio.run(cancel_on_signal(main()))
