from dataclasses import dataclass

from nostmack_hub.led_effect import LedEffect
from nostmack_hub.gear import Gear
from nostmack_hub.wled import LedValues


@dataclass
class LedEffectFixedCount:
    effect: LedEffect
    led_count: int

    def calculate(self, gear_values: list[int]):
        return self.effect.calculate(gear_values, self.led_count)


@dataclass
class LedValueCalculator(LedValues):
    gears: list[Gear]
    effect: LedEffectFixedCount

    def led_values(self):
        gear_values = [gear.value.inner for gear in self.gears]
        return self.effect.calculate(gear_values)
