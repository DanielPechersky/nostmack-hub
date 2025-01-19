import asyncio

from dataclasses import dataclass

from nostmack_hub.gear import Gear
from nostmack_hub.esp_listener import listen_to_esps
from nostmack_hub.wled import GetEffects, keep_wled_updated


def checked_getenv(var):
    import os

    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return value


# example: lights.local
WLED_ADDRESS = checked_getenv("WLED_ADDRESS")
LED_COUNT = int(checked_getenv("LED_COUNT"))


@dataclass
class GearEffects(GetEffects):
    gears: list[Gear]

    def get_effects(self) -> list[int]:
        def value_mapper(value):
            if value == 0:
                return 0
            if value == 255:
                return 255
            return round(value / 254 * 150) + 50

        return [value_mapper(g.value.inner) for g in self.gears]


async def main():
    esp_mapping = {
        0: Gear(5, 255),
        1: Gear(5, 255),
        2: Gear(5, 255),
    }
    gears = list(esp_mapping.values())

    async def update_effects(esp_values):
        async for esp_id, count in esp_values:
            gear = esp_mapping.get(esp_id)
            if gear is None:
                print(f"Received unknown ESP ID {esp_id}")
                continue
            print(f"id: {esp_id}, count: {count}")
            gear.turned(count)

    async with asyncio.TaskGroup() as tg:
        for gear in gears:
            tg.create_task(gear.discharge_task())

        tg.create_task(update_effects(listen_to_esps()))
        tg.create_task(
            keep_wled_updated(WLED_ADDRESS, LED_COUNT, GearEffects(gears=gears))
        )


if __name__ == "__main__":
    asyncio.run(main())
