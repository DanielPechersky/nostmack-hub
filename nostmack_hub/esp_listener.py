import struct

from nostmack_hub.udp import bind


async def listen_to_esps():
    async with bind(("0.0.0.0", 1234)) as socket:
        while True:
            bytes, _ = await socket.recv()

            (
                id,
                count,
            ) = struct.unpack("!ih", bytes)

            yield (id, count)
