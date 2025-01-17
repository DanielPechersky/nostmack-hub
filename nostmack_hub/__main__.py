import asyncio

import aiohttp

from nostmack_hub.effects import BrightnessEffect, EffectIntensityEffect
from nostmack_hub.esp_listener import EspListener
from nostmack_hub.wled import keep_wled_updated


def checked_getenv(var):
    import os

    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return value


# example: lights.local
WLED_ADDRESS = checked_getenv("WLED_ADDRESS")


async def main():
    brightness = BrightnessEffect(5)
    effect_intensity = EffectIntensityEffect(5)
    gear_listener = EspListener(
        {
            0: brightness,
            1: effect_intensity,
        }
    )

    async with asyncio.TaskGroup() as tg:
        tg.create_task(gear_listener.listen())
        tg.create_task(keep_wled_updated(WLED_ADDRESS, brightness, effect_intensity))


if __name__ == "__main__":
    asyncio.run(main())
