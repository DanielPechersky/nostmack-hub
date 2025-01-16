import asyncio

import aiohttp


WLED = "living.local"
UPDATE_FREQUENCY = 0.02


# gamma correction
# fmt: off
GAMMA = [
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


class GearListener:
    def __init__(self, sensitivity) -> None:
        self.values = [0, 0]
        self.sensitivity = sensitivity

    @property
    def brightness_value(self):
        return self.values[0]

    @property
    def effect_intensity_value(self):
        return self.values[1]

    def brightness(self) -> int:
        return boomerang(self.brightness_value)

    def effect_intensity(self) -> int:
        return boomerang(self.effect_intensity_value)

    def update_value(self, id, count):
        self.values[id] += count * self.sensitivity[id]
        self.values[id] %= 512

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
                self.update_value(id, count)

        await asyncio.start_server(callback, "0.0.0.0", 1234)


def boomerang(value: int) -> int:
    if value < 256:
        return value
    else:
        return 512 - 1 - value


async def main():
    gear_listener = GearListener(sensitivity=[5, 5])

    async with asyncio.TaskGroup() as tg, aiohttp.ClientSession() as session:
        tg.create_task(gear_listener.listen())

        try:
            while True:
                payload = {
                    "bri": GAMMA[gear_listener.brightness()],
                    "seg": {
                        "start": 0,
                        "stop": 300,
                        "sx": gear_listener.effect_intensity(),
                    },
                }
                print(f"New payload: {payload}")

                async with session.post(
                    f"http://{WLED}/json/state",
                    json=payload,
                ) as response:
                    if not response.ok:
                        print(f"Failed to talk to WLED: {response}")

                await asyncio.sleep(UPDATE_FREQUENCY)
        except KeyboardInterrupt:
            print("Brightness modulation stopped.")


if __name__ == "__main__":
    asyncio.run(main())
