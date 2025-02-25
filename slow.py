from nostmack_hub.led_effect import flowing_memento
from nostmack_hub.led_effect.gamma_correction import GammaCorrection
from nostmack_hub.led_value_calculator import LedEffectFixedCount
import sys
import cProfile


COLOURS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
LED_COUNT = 840


led_effect = GammaCorrection(
    flowing_memento.effect(COLOURS, LED_COUNT),
)
led_effect.calculate([1, 0, 0, 0, 0], LED_COUNT, 0)

profile = cProfile.Profile()
profile.enable()
led_effect.calculate([1, 0, 0, 0, 0], LED_COUNT, 30 * 60 * 1000)
profile.disable()
profile.dump_stats(sys.argv[1])
