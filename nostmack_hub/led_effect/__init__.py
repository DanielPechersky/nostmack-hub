import itertools
import math
from typing import Callable, Protocol
import random
from dataclasses import dataclass

from pygame.time import Clock

from nostmack_hub.gamma_correction import GAMMA_CORRECTION
from nostmack_hub.led_effect.animation import AnimatedValue, Animations, Dissapate, Ramp
from nostmack_hub.led_effect.colour import (
    Colour,
    add_colours,
    scale_colour,
    subtract_colours,
)


class LedEffect(Protocol):
    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        raise NotImplementedError


class StripedEffect(LedEffect):
    def __init__(self, colours: list[Colour]):
        self.colours = colours

    def calculate(self, gear_values: list[int], led_count: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        gear_values = scale_gear_values(gear_values)

        lights = [(0, 0, 0)] * led_count

        values_colours = itertools.cycle(zip(gear_values, self.colours, strict=True))

        for i in range(led_count):
            value, colour = next(values_colours)
            lights[i] = scale_colour(colour, value / 255)

        return lights


@dataclass
class StaticStripeEffect(LedEffect):
    inner: LedEffect
    colour: Colour
    stripe_width: int
    stripe_spacing: int
    offset: int = 0

    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        lights = self.inner.calculate(gear_values, led_count)
        for i in range(
            self.offset, len(lights), self.stripe_width + self.stripe_spacing
        ):
            for j in range(self.stripe_width):
                try:
                    lights[i + j] = self.colour
                except IndexError:
                    break
        return lights


def alternating_stripe_effect(
    left: LedEffect, left_width: int, right: LedEffect, right_width: int
):
    return LayeredEffect(
        [
            StaticStripeEffect(
                left,
                colour=(0, 0, 0),
                stripe_width=left_width,
                stripe_spacing=right_width,
            ),
            StaticStripeEffect(
                right,
                colour=(0, 0, 0),
                stripe_width=right_width,
                stripe_spacing=left_width,
                offset=left_width,
            ),
        ]
    )


class SectoredEffect(LedEffect):

    def __init__(self, colours: list[Colour]):
        self.colours = colours

    def calculate(self, gear_values: list[int], led_count: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        gear_values = scale_gear_values(gear_values)

        lights = [(0, 0, 0)] * led_count

        sector_length = math.ceil(led_count / len(self.colours))

        for sector, (value, colour) in enumerate(
            zip(gear_values, self.colours, strict=True)
        ):
            start = sector * sector_length
            end = (sector + 1) * sector_length
            for i in range(start, end):
                lights[i] = scale_colour(colour, value / 255)

        return lights


class ShimmerEffect(LedEffect):
    def __init__(self, colour: Colour):
        self.colour = colour

    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        return [scale_colour(self.colour, random.random()) for _ in range(led_count)]


def shimmer(effect, intensity: float):
    intensity = int(intensity * 255)
    return LayeredEffect(
        [effect, ShimmerEffect((intensity, intensity, intensity))],
        blending_fn=subtract_colours,
    )


class PulseOnFullChargeEffect(LedEffect):

    def __init__(self, colours: list[Colour]):
        self.colours = colours

        self.pulses: list[None | AnimatedValue] = [None] * len(self.colours)
        self.clock = Clock()

    def calculate(self, gear_values: list[int], led_count: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        dt = self.clock.tick()

        gear_values = scale_gear_values(gear_values)

        for pulse in self.pulses:
            if pulse is not None:
                pulse.tick(dt)

        lights = [(0, 0, 0)] * led_count

        for gear, (gear_value, colour) in enumerate(
            zip(gear_values, self.colours, strict=True)
        ):

            if gear_value == 255:
                if self.pulses[gear] is None:
                    self.pulses[gear] = AnimatedValue(
                        Animations([Ramp(400), Dissapate(1000)])
                    )
            else:
                self.pulses[gear] = None

            if (pulse := self.pulses[gear]) is not None:
                pulse_colour = scale_colour(colour, pulse.value())
                for i in range(len(lights)):
                    lights[i] = add_colours(lights[i], pulse_colour)

        return lights


@dataclass
class LayeredEffect(LedEffect):
    effects: list[LedEffect]
    blending_fn: Callable[[Colour, Colour], Colour] = add_colours

    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        effects = iter(self.effects)
        lights = next(effects).calculate(gear_values, led_count)

        for effect in effects:
            colours = effect.calculate(gear_values, led_count)
            lights = [
                self.blending_fn(light, colour)
                for light, colour in zip(lights, colours, strict=True)
            ]

        return lights


def scale_gear_values(gear_values):
    def value_mapper(value):
        if value == 0:
            return 0
        if value == 255:
            return 255
        return round(value / 254 * 150) + 50

    return list(map(value_mapper, gear_values))
