import asyncio


from nostmack_hub.led_effect import StripedEffect
from nostmack_hub.gear import Gear
from nostmack_hub.machine import Machine
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
    esp_mapping = parse_gears(GEARS)
    assert len(esp_mapping) == 3, "The current effect only supports exactly 3 gears"
    machine = Machine(
        esp_mapping=esp_mapping,
        wled=Wled(WLED_ADDRESS),
        effect=StripedEffect([(255, 0, 0), (0, 0, 255), (127, 0, 127)], LED_COUNT),
    )

    await machine.run()


def parse_gears(gears):
    def parse_gear(gear):
        esp_id, sensitivity = gear.split(":")
        return int(esp_id), Gear(int(sensitivity))

    return dict(map(parse_gear, gears.split(",")))


if __name__ == "__main__":
    asyncio.run(main())
