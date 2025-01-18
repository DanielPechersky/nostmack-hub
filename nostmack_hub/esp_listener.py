import asyncio
from typing import Mapping

from nostmack_hub.effects import Effect


async def listen_to_esps(effects: Mapping[int, Effect]):
    async def callback(reader, _writer):
        import struct

        id = await reader.readexactly(4)
        (id,) = struct.unpack("!i", id)
        print(f"Connected to gear with ID {id}")

        while True:
            bytes = await reader.readexactly(2)
            (count,) = struct.unpack("!h", bytes)
            print(f"ID {id} count: {count}")
            effects[id].update(count)

    await asyncio.start_server(callback, "0.0.0.0", 1234)
