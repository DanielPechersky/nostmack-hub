import asyncio

from nostmack_hub.effects import PeakingEffect
from nostmack_hub.esp_listener import listen_to_esps
from nostmack_hub.wled import keep_wled_updated


def checked_getenv(var):
    import os

    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return value


# example: lights.local
WLED_ADDRESS = checked_getenv("WLED_ADDRESS")
LED_COUNT = int(checked_getenv("LED_COUNT"))


async def main():
    esp_mapping = {
        0: PeakingEffect(5, 255),
        1: PeakingEffect(5, 255),
        2: PeakingEffect(5, 255),
    }
    effects = list(esp_mapping.values())

    async with asyncio.TaskGroup() as tg:
        for effect in effects:
            tg.create_task(effect.decay_task())

        tg.create_task(listen_to_esps(esp_mapping))
        tg.create_task(keep_wled_updated(WLED_ADDRESS, LED_COUNT, effects))


if __name__ == "__main__":
    asyncio.run(main())
