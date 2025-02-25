from dataclasses import dataclass
import random

import numpy as np

from nostmack_hub.led_effect import LedEffect, scale_gear_values
from nostmack_hub.led_effect.animation import AnimatedValue, Animations, Dissapate, Ramp
from nostmack_hub.led_effect.colour import Colour, add_colours, scale_colour


@dataclass
class SeedConfig:
    influence_size: int
    ramp_time: int
    dissapate_time: int


SEED_FREQUENCY = 50


class BlorpEffect(LedEffect):

    def __init__(self, colours: list[Colour], led_count: int, seed_config: SeedConfig):
        self.colours = colours
        self.led_count = led_count
        self.seed_config = seed_config

        self.seeds: list[Seed] = []
        total_time = seed_config.ramp_time + seed_config.dissapate_time
        self.max_seeds = total_time / SEED_FREQUENCY
        self.time_since_last_seed_planted: int = 0

    def plant_new_seed(self):
        if len(self.seeds) >= self.max_seeds:
            return

        gear = random.randrange(len(self.colours))

        cluster_center = self.led_count // len(self.colours) * gear

        position = cluster_center + int(random.gauss(sigma=self.led_count / 16))
        position %= self.led_count

        dissapate_time = self.seed_config.dissapate_time + int(random.gauss(sigma=1000))

        self.seeds.append(
            Seed(
                position,
                gear,
                influence_size=self.seed_config.influence_size,
                animated_intensity=AnimatedValue(
                    Animations(
                        [Ramp(self.seed_config.ramp_time), Dissapate(dissapate_time)]
                    )
                ),
            )
        )

    def calculate(self, gear_values: list[int], led_count: int, delta_time: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"
        assert self.led_count == led_count

        self.time_since_last_seed_planted += delta_time

        self.seeds = [seed for seed in self.seeds if not seed.done]
        while self.time_since_last_seed_planted > SEED_FREQUENCY:
            self.plant_new_seed()
            self.time_since_last_seed_planted -= SEED_FREQUENCY

        gear_values = scale_gear_values(gear_values)

        layers = []

        for seed in self.seeds:
            seed.animated_intensity.tick(delta_time)

        for gear, (gear_value, colour) in enumerate(
            zip(gear_values, self.colours, strict=True)
        ):
            layer = [(0, 0, 0)] * self.led_count

            for seed in self.seeds:
                if seed.gear == gear:
                    influence = seed.influence()
                    colours = [
                        scale_colour(colour, intensity) for intensity in influence
                    ]
                    for i, c in enumerate(colours, start=seed.position):
                        i = i % len(layer)
                        layer[i] = add_colours(layer[i], c)

            layer = [scale_colour(colour, gear_value / 255) for colour in layer]

            layers.append(layer)

        lights = [(0, 0, 0)] * self.led_count

        for i in range(self.led_count):
            for layer in layers:
                lights[i] = add_colours(lights[i], layer[i])

        return lights


@dataclass
class Seed:
    position: int
    gear: int

    influence_size: int

    animated_intensity: AnimatedValue

    @property
    def done(self):
        return self.animated_intensity.finished_animating

    def intensity(self) -> float:
        return self.animated_intensity.value()

    @property
    def influence_center(self):
        return self.influence_size // 2

    def influence(self):
        values = np.arange(self.influence_size)
        a = (self.influence_size / 2) ** -2
        return (1.0 - a * (self.influence_center - values) ** 2).clip(
            min=0
        ) * self.intensity()
