import asyncio
import struct
from typing import Mapping

from nostmack_hub.effects import Effect
from nostmack_hub.udp import bind


async def listen_to_esps(effects: Mapping[int, Effect]):
    async with bind(("0.0.0.0", 1234)) as socket:
        while True:
            bytes, _ = await socket.recv()

            (
                id,
                count,
            ) = struct.unpack("!ih", bytes)

            print(f"ID {id} count: {count}")
            effects[id].update(count)
