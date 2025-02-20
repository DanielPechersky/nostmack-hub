from nostmack_hub.led_effect import (
    LayeredEffect,
    PulseOnFullChargeEffect,
    StripedEffect,
    alternating_stripe_effect,
)
from nostmack_hub.led_effect.blorp_effect import BlorpEffect, SeedConfig


def effect(colours, led_count):
    return LayeredEffect(
        [
            PulseOnFullChargeEffect(colours),
            alternating_stripe_effect(
                StripedEffect(colours),
                5,
                BlorpEffect(
                    colours,
                    led_count,
                    SeedConfig(influence_size=31, ramp_time=500, dissapate_time=5000),
                ),
                20,
            ),
        ],
    )
