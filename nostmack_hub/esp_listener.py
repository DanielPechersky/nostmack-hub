import struct

from nostmack_hub import esp_diagnostics
from nostmack_hub.udp import bind


async def listen_to_esps():
    async with (
        bind(("0.0.0.0", 1234)) as socket,
        esp_diagnostics.start(time_between_prints=1) as diagnostics,
    ):
        while True:
            bytes, _ = await socket.recv()

            (
                id,
                count,
            ) = struct.unpack("!ih", bytes)

            diagnostics.seen(id)

            yield (id, count)
