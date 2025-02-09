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


async def main():
    esp_mapping = {
        0: Gear(5, 255),
        1: Gear(5, 255),
        2: Gear(5, 255),
    }
    machine = Machine(
        esp_mapping=esp_mapping,
        wled=Wled(WLED_ADDRESS),
        effect=StripedEffect([(255, 0, 0), (0, 0, 255), (127, 0, 127)], LED_COUNT),
    )

    await machine.run()


if __name__ == "__main__":
    asyncio.run(main())
