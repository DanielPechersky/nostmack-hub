from dataclasses import dataclass
from nostmack_hub.gamma_correction import GAMMA_CORRECTION
from nostmack_hub.led_effect import LedEffect
from nostmack_hub.led_effect.colour import map_colour


@dataclass
class GammaCorrection(LedEffect):
    inner: LedEffect

    def calculate(self, gear_values: list[int], led_count):
        lights = self.inner.calculate(gear_values, led_count)

        lights = [
            map_colour(light, lambda channel: GAMMA_CORRECTION[channel])
            for light in lights
        ]

        return lights
