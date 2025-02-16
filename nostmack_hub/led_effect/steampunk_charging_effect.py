# A dictionary of named colors → (R, G, B)
import math
import random
from nostmack_hub.led_effect import LedEffect
from nostmack_hub.led_effect.colour import Colour


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
