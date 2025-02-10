import asyncio

import random
from pygame.mixer import Sound

from nostmack_hub.gear import Gear


class Sounds:
    def __init__(self, gears: list[Gear], sounds: list[Sound]):
        self.gears = gears
        self.sounds = sounds

    async def play_sounds(self):
        sounds = random.sample(self.sounds, len(self.gears))
        try:
            for sound in sounds:
                sound.play(loops=-1)
            while True:
                await asyncio.sleep(0.1)
                for gear, sound in zip(self.gears, sounds, strict=True):
                    volume = gear.value.inner / 255
                    sound.set_volume(volume)
        except asyncio.CancelledError:
            for sound in sounds:
                sound.fadeout(500)
