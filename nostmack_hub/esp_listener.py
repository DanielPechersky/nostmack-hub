import asyncio

from nostmack_hub.effects import Effect


class EspListener:
    def __init__(self, effects: dict[int, Effect]) -> None:
        self.effects = effects

    async def listen(self):
        async def callback(reader, _writer):
            import struct

            id = await reader.readexactly(4)
            (id,) = struct.unpack("!i", id)
            print(f"Connected to gear with ID {id}")

            while True:
                bytes = await reader.readexactly(2)
                (count,) = struct.unpack("!h", bytes)
                print(f"ID {id} count: {count}")
                self.effects[id].update(count)

        await asyncio.start_server(callback, "0.0.0.0", 1234)
