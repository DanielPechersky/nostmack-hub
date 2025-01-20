import asyncio
import itertools
from typing import Protocol

import aiohttp
from dataclasses import dataclass

from nostmack_hub.dnrgb import dnrgb_packets
from nostmack_hub.udp import connect


UPDATE_FREQUENCY = 0.02


class GetEffects(Protocol):
    def get_effects(self) -> list[int]:
        raise NotImplemented


@dataclass
class Wled:
    address: str
    led_count: int

    async def set_preset(self, preset: int):
        async with aiohttp.ClientSession(
            base_url=f"http://{self.address}/json/state/",
            raise_for_status=True,
        ) as session:
            async with session.post("", json={"ps": preset, "lor": 1}) as response:
                pass

    async def set_live(self):
        async with aiohttp.ClientSession(
            base_url=f"http://{self.address}/json/state/",
            raise_for_status=True,
        ) as session:
            async with session.post("", json={"lor": 0}) as response:
                pass

    async def keep_updated(self, effects: GetEffects):
        async with connect((self.address, 21324)) as socket:
            while True:
                await update_wled(socket, self.led_count, effects.get_effects())
                await asyncio.sleep(UPDATE_FREQUENCY)


async def update_wled(socket, led_count, effect_values: list[int]):
    lights = create_rgb_array(led_count, effect_values)

    for packet in dnrgb_packets(lights):
        await socket.send(packet)


def create_rgb_array(
    led_count: int, effect_values: list[int]
) -> list[tuple[int, int, int]]:
    colours = [(255, 0, 0), (0, 0, 255), (127, 0, 127)]

    def scale_colour(colour, intensity):
        return tuple(round(channel * intensity) for channel in colour)

    lights = [(0, 0, 0)] * 50

    values_colours = itertools.cycle(zip(effect_values, colours, strict=True))

    for i in range(0, led_count):
        value, colour = next(values_colours)
        lights[i] = scale_colour(colour, value / 255)

    lights = [tuple(GAMMA_CORRECTION[channel] for channel in light) for light in lights]

    return lights


# fmt: off
GAMMA_CORRECTION = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99, 101, 102, 104, 105, 107, 109, 110, 112, 114,
    115, 117, 119, 120, 122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142,
    144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
    177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213,
    215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244, 247, 249, 252, 255
]
# fmt: on
