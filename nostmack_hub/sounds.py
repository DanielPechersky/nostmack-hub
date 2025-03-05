import asyncio

import random
from pygame.mixer import Sound

from nostmack_hub.gear import Gear


class Sounds:
    def __init__(self, gears: list[Gear], sounds: list[Sound], ding: Sound):
        self.gears = gears
        self.sounds = sounds
        self.ding = ding

    async def play_sounds(self):
        sounds = random.sample(self.sounds, len(self.gears))
        try:
            for sound in sounds:
                sound.play(loops=-1)
                sound.set_volume(0)
            dinged = [False] * len(self.gears)
            while True:
                await asyncio.sleep(0.1)
                for i, (gear, sound) in enumerate(zip(self.gears, sounds, strict=True)):
                    volume = gear.value.inner / 255
                    sound.set_volume(volume)

                    if gear.value.is_max:
                        if not dinged[i]:
                            self.ding.play()
                            dinged[i] = True
                    else:
                        dinged[i] = False

        except asyncio.CancelledError:
            for sound in sounds:
                sound.fadeout(500)
