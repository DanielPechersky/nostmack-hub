import itertools
import math
from typing import Protocol

from dataclasses import dataclass

from nostmack_hub.gamma_correction import GAMMA_CORRECTION


Colour = tuple[int, int, int]


class LedEffect(Protocol):
    def calculate(self, gear_values: list[int]) -> list[Colour]:
        raise NotImplementedError


class StripedEffect(LedEffect):
    def __init__(self, colours: list[Colour], led_count: int):
        self.colours = colours
        self.led_count = led_count

    def calculate(self, gear_values: list[int]):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        gear_values = scale_gear_values(gear_values)

        lights = [(0, 0, 0)] * self.led_count

        values_colours = itertools.cycle(zip(gear_values, self.colours, strict=True))

        for i in range(0, self.led_count):
            value, colour = next(values_colours)
            lights[i] = scale_colour(colour, value / 255)

        return lights


class SectoredEffect(LedEffect):

    def __init__(self, colours: list[Colour], led_count: int):
        self.colours = colours
        self.led_count = led_count

    def calculate(self, gear_values: list[int]):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        gear_values = scale_gear_values(gear_values)

        lights = [(0, 0, 0)] * self.led_count

        sector_length = math.ceil(self.led_count / len(self.colours))

        for sector, (value, colour) in enumerate(
            zip(gear_values, self.colours, strict=True)
        ):
            start = sector * sector_length
            end = (sector + 1) * sector_length
            for i in range(start, end):
                lights[i] = scale_colour(colour, value / 255)

        return lights


@dataclass
class GammaCorrection(LedEffect):
    inner: LedEffect

    def calculate(self, gear_values: list[int]):
        lights = self.inner.calculate(gear_values)

        lights = [
            map_colour(light, lambda channel: GAMMA_CORRECTION[channel])
            for light in lights
        ]

        return lights


def scale_colour(colour, intensity):
    return map_colour(colour, lambda channel: round(channel * intensity))


def scale_gear_values(gear_values):
    def value_mapper(value):
        if value == 0:
            return 0
        if value == 255:
            return 255
        return round(value / 254 * 150) + 50

    return list(map(value_mapper, gear_values))


def map_colour(colour: Colour, f) -> Colour:
    return (f(colour[0]), f(colour[1]), f(colour[2]))
