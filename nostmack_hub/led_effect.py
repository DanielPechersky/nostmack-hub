import itertools
import math
from typing import Callable, Protocol
import random
from dataclasses import dataclass

from pygame.time import Clock

from nostmack_hub.gamma_correction import GAMMA_CORRECTION


Colour = tuple[int, int, int]


class LedEffect(Protocol):
    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        raise NotImplementedError


# A dictionary of named colors → (R, G, B)
named_colors: dict[str, Colour] = {
    "Cherenkov Radiation": (34, 189, 251),
    "Red Alert": (208, 52, 44),
    "Sky Blue": (135, 206, 235),
    "Safety Orange": (255, 121, 0),
    "Dark Red": (139, 0, 0),
    "Radioactive Green": (128, 180, 37),
    "Medium Purple": (147, 112, 219),
    "Purple": (128, 0, 128),
    "Dark Magenta": (139, 0, 139),
    "Magenta 3": (205, 0, 205),
    "Magenta 2": (238, 0, 238),
    "Magenta": (255, 0, 255),
    "Orchid 4": (139, 71, 137),
    "Orchid 3": (205, 105, 201),
    "Orchid 2": (238, 122, 233),
    "Orchid 1": (255, 131, 250),
    "Orchid": (218, 112, 214),
    "Dark Purple": (135, 31, 120),
    "Purple Fish": (178, 114, 166),
    "Medium Purple 4": (93, 71, 139),
    "Medium Purple 3": (137, 104, 205),
    "Medium Purple 2": (159, 121, 238),
    "Yellow 4": (139, 139, 0),
    "Bright Gold Yellow": (217, 217, 25),
    "Yellow 3": (205, 205, 0),
    "Mustard": (255, 204, 17),  # first usage
    "Gold": (255, 215, 0),
    "Gold 4": (139, 117, 0),
    "Gold 3": (205, 173, 0),
    "Gold 2": (238, 201, 0),
    "Gummy Yellow": (251, 219, 12),
    "Mustard 2": (255, 204, 17),  # second usage
    "Banana": (227, 207, 87),
    "Pineapple": (252, 220, 59),
    "Sign Yellow": (252, 209, 22),
    "Golden Rod": (219, 219, 112),
    "Yellow": (255, 255, 0),
    "Ivory Yellow": (255, 255, 240),
    "Yellow 2": (238, 238, 0),
    "Olive Drab 1": (192, 255, 62),
    "Leaf Green": (85, 174, 58),
    "Nerf Green": (73, 226, 14),
    "LED Green": (93, 252, 10),
    "Guacamole Green": (166, 215, 133),
    "Chartreuse Green": (127, 255, 0),
    "Chartreuse 2 Green": (118, 238, 0),
    "Chartreuse 3 Green": (102, 205, 0),
    "Chartreuse 4 Green": (69, 139, 0),
    "Dark Olive Green 1": (202, 255, 112),
    "Dark Olive Green 2": (188, 238, 104),
    "Dark Olive Green 3": (162, 205, 90),
    "Dark Olive Green 4": (110, 139, 61),
    "Olive Drab 2": (179, 238, 58),
    "Pear Green": (209, 226, 49),
    "Celery Green": (207, 215, 132),
    "Iceberg Lettuce Green": (205, 228, 114),
    "Gold Green": (170, 221, 0),
    "Wasabi Green": (174, 187, 81),
    "Fire Truck Green": (205, 215, 4),
    "Light Yellow": (255, 255, 224),
    "Navy Blue": (35, 35, 142),
    "Diamond Blue": (14, 191, 233),
    "NYPD Blue": (57, 183, 205),
    "Cerulean": (5, 184, 204),
    "Indiglo": (5, 233, 255),
    "Turquoise 1": (0, 245, 255),
    "Turquoise 2": (0, 229, 238),
    "Turquoise 3": (0, 197, 205),
    "Turquoise 4": (0, 134, 139),
    "Cadet Blue": (95, 158, 160),
    "Deep Sky Blue 4": (0, 104, 139),
    "Deep Sky Blue 3": (0, 154, 205),
    "Deep Sky Blue 2": (0, 178, 238),
    "Deep Sky Blue": (0, 191, 255),
    "Steel Blue": (35, 107, 142),
    "Pacific Blue": (53, 88, 108),
    "Blue Mist": (130, 207, 253),
    "Aquamarine": (78, 120, 160),
    "Slate Blue": (0, 127, 255),
    "Blue": (0, 0, 255),
    "Blue 2": (0, 0, 238),
    "Medium Blue": (0, 0, 205),
    "Surf Blue": (99, 209, 244),
    "Tangerine": (255, 114, 22),
    "Cadium Deep Red": (227, 23, 13),
    "Orange Red": (255, 64, 64),
    "FireBrick Red": (178, 34, 34),
    "Red1": (255, 0, 0),
    "Red2": (238, 0, 0),
    "Mandarin Orange": (228, 120, 51),
    "Red3": (205, 0, 0),
    "Darkred (SVG)": (139, 0, 0),
    "Maroon (16 SVG)": (176, 0, 0),
    "Scarlet": (140, 23, 23),
    "Firebrick (SVG)": (178, 34, 34),
    "Orange": (204, 50, 50),
    "Strawberry": (190, 38, 37),
    "Soylent Red": (224, 64, 6),
    "Brown": (128, 42, 42),
    "Dark Salmon (SVG)": (233, 150, 122),
    "Red Delicious": (157, 19, 9),
    "Salmon 1": (255, 140, 105),
    "Salmon 2": (238, 130, 98),
    "Blood Orange": (204, 17, 0),
    "Orange Crush": (248, 117, 49),
}


class SteampunkChargingEffect(LedEffect):
    def __init__(
        self,
        colours: list[Colour],
        turn: float = 1.0,
        max_spread: float = 1.0,
        min_brightness: int = 40,
    ):
        self.colours = colours
        self.turn = turn
        self.max_spread = max_spread
        self.min_brightness = min_brightness

        # 1) Evenly distribute gear centers around the circle, plus a small random jitter.
        self._centers = []
        num_gears = len(colours)
        for i in range(num_gears):
            base_angle = (2.0 * math.pi * i) / num_gears
            jittered_angle = base_angle + random.uniform(-0.2, 0.2)
            jittered_angle %= 2.0 * math.pi
            self._centers.append(jittered_angle)

        # 2) Random exponent factor per gear for “liquidy” fade.
        self._exp_factors = [random.uniform(1.5, 2.5) for _ in range(num_gears)]

        # 3) Predefine or dynamically store overlap colors.
        self._overlap_colors_map: dict[frozenset[int], Colour] = {
            # overlap color for gears 0 & 1
            frozenset([0, 1]): (255, 128, 64),
            # overlap color for gears 0 & 2
            frozenset([0, 2]): (128, 255, 64),
            # overlap color for gears 1 & 2
            frozenset([1, 2]): (64, 128, 255),
            # ... add more known combos if needed ...
        }
        # Fallback color for any overlap not in the map:
        self._fallback_overlap_color: Colour = (180, 100, 200)

        # Cache that ensures stable overlap color across frames:
        self._overlap_colors: dict[frozenset[int], Colour] = {}

    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        """
        Returns the LED strip as a list of (r, g, b).
        """
        if all(value == 0 for value in gear_values):
            return [(0, 0, 0) for _ in range(led_count)]

        # aggregator[i] = dict {gear_index -> brightness} for LED i
        aggregator = [dict() for _ in range(led_count)]

        # ────────── Compute partial brightness for each gear ──────────
        for gear_index, gear_value in enumerate(gear_values):
            if gear_value <= 0:
                continue

            center_angle = self._centers[gear_index]
            exp_factor = self._exp_factors[gear_index]

            fraction = min(1.0, gear_value / (self.turn * 255.0))
            spread = fraction * (self.max_spread * (math.pi / 2))
            center_brightness = self.min_brightness + fraction * (
                255 - self.min_brightness
            )

            for led_i in range(led_count):
                angle_i = (2.0 * math.pi * led_i) / led_count
                diff = abs(angle_i - center_angle)
                angular_dist = min(diff, 2.0 * math.pi - diff)

                if angular_dist <= spread:
                    # "Liquidy" fade
                    norm_dist = angular_dist / spread
                    fade_factor = 1.0 - (norm_dist**exp_factor)
                    fade_factor = max(min(fade_factor, 1.0), 0.0)
                    brightness = self.min_brightness + fade_factor * (
                        center_brightness - self.min_brightness
                    )
                    aggregator[led_i][gear_index] = brightness

        # ────────── Build final LED list ──────────
        final_leds: list[Colour] = []
        for led_i in range(led_count):
            gears_here = aggregator[led_i]
            if not gears_here:
                final_leds.append((0, 0, 0))
                continue

            gear_set = frozenset(gears_here.keys())
            if len(gear_set) == 1:
                # Single gear -> scale that gear’s color
                gidx = next(iter(gear_set))
                brightness = gears_here[gidx]
                base_r, base_g, base_b = self.colours[gidx]
                scale = brightness / 255.0
                r = int(base_r * scale)
                g = int(base_g * scale)
                b = int(base_b * scale)
                final_leds.append((r, g, b))

            else:
                # Multiple gears -> single stable color, brightness from sum
                overlap_color = self._get_overlap_color(gear_set)
                total_brightness = sum(gears_here.values())
                if total_brightness > 255:
                    total_brightness = 255
                scale = total_brightness / 255.0

                or_, og_, ob_ = overlap_color
                r = int(or_ * scale)
                g = int(og_ * scale)
                b = int(ob_ * scale)
                final_leds.append((r, g, b))

        return final_leds

    # ─────────────────────────────────────────────
    # Overlap-Color Calculation
    # ─────────────────────────────────────────────
    def _get_overlap_color(self, gear_set: frozenset[int]) -> Colour:
        """
        Picks a stable “nice” color for any multi-gear overlap.
        We do NOT do invert/hue-shift here — instead we either:
          1) Look up in a known dictionary of combos, or
          2) Use a fallback if not in that dictionary.
        """
        if gear_set in self._overlap_colors:
            return self._overlap_colors[gear_set]

        # Check if the gear_set is in our pre-defined combos:
        if gear_set in self._overlap_colors_map:
            color = self._overlap_colors_map[gear_set]
        else:
            # If not in map, use fallback (or random from a palette)
            color = self._fallback_overlap_color

        self._overlap_colors[gear_set] = color
        return color


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
                lights[i + j] = self.colour
        return lights


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


@dataclass
class SeedConfig:
    influence_size: int
    ramp_time: int
    dissapate_time: int


@dataclass
class RampDissapate:
    ramp_time: int
    dissapate_time: int

    @property
    def total_time(self):
        return self.ramp_time + self.dissapate_time

    def done(self, progress):
        return progress >= self.total_time

    def intensity(self, progress):
        ramp_up_time = self.ramp_time
        dissapate_time = self.dissapate_time

        if progress < ramp_up_time:
            return progress / ramp_up_time
        progress -= ramp_up_time

        return max(dissapate_time - progress, 0) / dissapate_time


@dataclass
class Pulse:
    ramp_dissapate: RampDissapate

    progress: int = 0

    @property
    def total_time(self):
        return self.ramp_dissapate.total_time

    @property
    def done(self):
        return self.ramp_dissapate.done(self.progress)

    @property
    def intensity(self) -> float:
        return self.ramp_dissapate.intensity(self.progress)


@dataclass
class Seed:
    position: int
    gear: int

    influence_size: int
    ramp_dissapate: RampDissapate

    progress: int = 0

    @property
    def influence_center(self):
        return self.influence_size // 2

    @property
    def total_time(self):
        return self.ramp_dissapate.total_time

    @property
    def is_expired(self):
        return self.ramp_dissapate.done(self.progress)

    @property
    def intensity(self) -> float:
        return self.ramp_dissapate.intensity(self.progress)

    def influence_fn(self, position: int) -> float:
        a = (self.influence_size / 2) ** -2
        return (
            max(1.0 - a * ((self.influence_center - position)) ** 2, 0) * self.intensity
        )

    def influence(self):
        return [self.influence_fn(p) for p in range(self.influence_size)]


class PulseOnFullChargeEffect(LedEffect):

    def __init__(self, colours: list[Colour]):
        self.colours = colours

        self.pulses: list[None | Pulse] = [None] * len(self.colours)
        self.clock = Clock()

    def calculate(self, gear_values: list[int], led_count: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"

        dt = max(self.clock.tick(), 100)

        gear_values = scale_gear_values(gear_values)

        for pulse in self.pulses:
            if pulse is not None and not pulse.done:
                pulse.progress += dt

        lights = [(0, 0, 0)] * led_count

        for gear, (gear_value, colour) in enumerate(
            zip(gear_values, self.colours, strict=True)
        ):

            if gear_value == 255:
                if self.pulses[gear] is None:
                    self.pulses[gear] = Pulse(
                        RampDissapate(ramp_time=1000, dissapate_time=3000)
                    )
            else:
                self.pulses[gear] = None

            if (pulse := self.pulses[gear]) is not None:
                pulse_colour = scale_colour(colour, pulse.intensity)
                for i in range(len(lights)):
                    lights[i] = add_colours(lights[i], pulse_colour)

        return lights


class BlorpEffect(LedEffect):

    def __init__(self, colours: list[Colour], led_count: int, seed_config: SeedConfig):
        self.colours = colours
        self.led_count = led_count
        self.seed_config = seed_config

        self.seeds: list[Seed] = []
        self.time_since_last_seed_planted: int = 0
        self.clock = Clock()

    def plant_new_seed(self):
        gear = random.randrange(len(self.colours))

        cluster_center = self.led_count // len(self.colours) * gear

        position = cluster_center + int(random.gauss(sigma=self.led_count / 8))
        position %= self.led_count

        dissapate_time = self.seed_config.dissapate_time + int(random.gauss(sigma=1000))

        self.seeds.append(
            Seed(
                position,
                gear,
                influence_size=self.seed_config.influence_size,
                ramp_dissapate=RampDissapate(
                    self.seed_config.ramp_time, dissapate_time
                ),
            )
        )

    def calculate(self, gear_values: list[int], led_count: int):
        assert len(gear_values) == len(
            self.colours
        ), "Received wrong number of gear values"
        assert self.led_count == led_count

        dt = max(self.clock.tick(), 100)
        self.time_since_last_seed_planted += dt

        SEED_FREQUENCY = 50
        while self.time_since_last_seed_planted > SEED_FREQUENCY:
            self.plant_new_seed()
            self.time_since_last_seed_planted -= SEED_FREQUENCY

        gear_values = scale_gear_values(gear_values)

        layers = []

        for seed in self.seeds:
            seed.progress += dt

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

        self.seeds = [seed for seed in self.seeds if not seed.is_expired]

        return lights


def add_colours(a: Colour, b: Colour) -> Colour:
    return map_colour((a[0] + b[0], a[1] + b[1], a[2] + b[2]), lambda c: min(c, 255))


@dataclass
class LayeredEffect(LedEffect):
    effects: list[LedEffect]
    blending_fn: Callable[[Colour, Colour], Colour] = add_colours

    def calculate(self, gear_values: list[int], led_count: int) -> list[Colour]:
        lights = [(0, 0, 0)] * led_count

        for effect in self.effects:
            colours = effect.calculate(gear_values, led_count)
            lights = [
                add_colours(light, colour)
                for light, colour in zip(lights, colours, strict=True)
            ]

        return lights


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
