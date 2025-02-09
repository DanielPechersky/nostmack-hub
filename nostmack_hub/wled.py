import asyncio
from typing import Protocol

import aiohttp
from dataclasses import dataclass

from nostmack_hub.dnrgb import dnrgb_packets
from nostmack_hub.udp import connect


UPDATE_FREQUENCY = 0.02


class LedValues(Protocol):
    def led_values(self) -> list[tuple[int, int, int]]:
        raise NotImplementedError


@dataclass
class Wled:
    address: str

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

    async def keep_updated(self, led_values: LedValues):
        async with connect((self.address, 21324)) as socket:
            while True:
                await update_wled(socket, led_values.led_values())
                await asyncio.sleep(UPDATE_FREQUENCY)


async def update_wled(socket, leds: list[tuple[int, int, int]]):
    for packet in dnrgb_packets(leds):
        await socket.send(packet)
