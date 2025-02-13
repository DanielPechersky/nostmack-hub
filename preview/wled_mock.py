import asyncio
from dataclasses import dataclass
from nostmack_hub.led_effect import Colour
from nostmack_hub.wled import LedValues, WledProtocol


@dataclass
class WledPreset:
    number: int


@dataclass
class WledRealtime:
    leds: list[Colour]


class WledMock(WledProtocol):
    state: WledPreset | WledRealtime

    def __init__(self):
        self.state = WledPreset(1)

    async def set_preset(self, preset: int):
        self.state = WledPreset(preset)

    async def set_live(self):
        pass

    async def keep_updated(self, led_values: LedValues):
        while True:
            self.state = WledRealtime(led_values.led_values())
            await asyncio.sleep(1 / 120)
