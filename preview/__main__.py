import asyncio
from contextlib import contextmanager
from pathlib import Path

from imgui_bundle import imgui, imgui_ctx, hello_imgui
import dotenv
import pygame

from nostmack_hub.led_effect import (
    LayeredEffect,
    LedEffect,
    PulseOnFullChargeEffect,
    SectoredEffect,
    StripedEffect,
    alternating_stripe_effect,
    shimmer,
)
from nostmack_hub.led_effect.blorp_effect import BlorpEffect, SeedConfig
from nostmack_hub.led_effect.steampunk_charging_effect import SteampunkChargingEffect
from nostmack_hub.led_value_calculator import LedEffectFixedCount
from preview.init_machine import init_machine
from preview.draw_leds import draw_coloured_line
from preview.wled_mock import WledPreset, WledRealtime

dotenv.load_dotenv("config.env")


COLOURS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]


def checked_getenv(var):
    import os

    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not set.")
    return value


LED_COUNT = int(checked_getenv("LED_COUNT"))

SOUND_POOL = Path(checked_getenv("SOUND_POOL"))
SOUND_DING = Path(checked_getenv("SOUND_DING"))
SOUND_FINALE = Path(checked_getenv("SOUND_FINALE"))

EFFECTS: list[LedEffect] = [
    StripedEffect(COLOURS),
    SectoredEffect(COLOURS),
    SteampunkChargingEffect(COLOURS),
    LayeredEffect(
        [
            PulseOnFullChargeEffect(COLOURS),
            alternating_stripe_effect(
                StripedEffect(COLOURS),
                5,
                BlorpEffect(
                    COLOURS,
                    LED_COUNT,
                    SeedConfig(influence_size=31, ramp_time=500, dissapate_time=5000),
                ),
                5,
            ),
        ],
    ),
]


async def main():
    with init_pygame_mixer():

        selected_effect_index = 0

        def selected_effect():
            return LedEffectFixedCount(EFFECTS[selected_effect_index], LED_COUNT)

        machine, esp_events, wled = init_machine(
            selected_effect(),
            SOUND_POOL,
            SOUND_DING,
            SOUND_FINALE,
        )

        gear_turns = {esp_id: 0.0 for esp_id, _ in machine.esp_mapping.items()}

        clock = pygame.time.Clock()

        def gui():
            nonlocal selected_effect_index

            dt = clock.tick() / 1000

            with imgui_ctx.begin("Settings"):
                imgui.set_window_pos((550, 0), imgui.Cond_.first_use_ever.value)

                for i, gear in machine.esp_mapping.items():
                    imgui.text(f"Gear {i}: {gear.value.inner}")
                    imgui.button(f"Slow turn {i}")
                    if imgui.is_item_hovered():
                        gear_turns[i] += dt * 10
                    imgui.same_line()
                    imgui.button(f"Fast turn {i}")
                    if imgui.is_item_hovered():
                        gear_turns[i] += dt * 50

                _, value = imgui.list_box(
                    "Effect",
                    selected_effect_index,
                    [effect.__class__.__name__ for effect in EFFECTS],
                )
                selected_effect_index = value
                imgui.text("note: machine must not be charging to change effects")

                if imgui.button("Reset machine"):
                    machine.state.to_initial()
                    for gear in machine.gears:
                        gear.reset()

            for i, turn in gear_turns.items():
                sensed_turns = round(turn)
                gear_turns[i] -= sensed_turns
                esp_events.append((i, sensed_turns))

            machine.effect = selected_effect()

            with imgui_ctx.begin("Pattern"):
                imgui.set_window_pos((0, 0), imgui.Cond_.first_use_ever.value)
                imgui.set_window_size((550, 550), imgui.Cond_.first_use_ever.value)

                match wled.state:
                    case WledPreset(id):
                        imgui.text(f"Preset id: {id}")
                    case WledRealtime(leds):
                        draw_list = imgui.get_window_draw_list()
                        wx, wy = imgui.get_window_pos()

                        side_length = round(len(leds) * 3 / 10)
                        top_length = round(len(leds) * 2 / 10)

                        right_leds = leds[:side_length]
                        bottom_leds = leds[side_length:][:top_length]
                        left_leds = leds[side_length + top_length :][:side_length]
                        top_leds = leds[side_length + top_length + side_length :]

                        tl_x, tl_y = 30, 30
                        br_x, br_y = 500, 500

                        draw_coloured_line(
                            draw_list,
                            right_leds,
                            (wx + br_x, wy + tl_y),
                            (wx + br_x, wy + br_y),
                        )

                        draw_coloured_line(
                            draw_list,
                            bottom_leds,
                            (wx + br_x, wy + br_y),
                            (wx + tl_x, wy + br_y),
                        )

                        draw_coloured_line(
                            draw_list,
                            left_leds,
                            (wx + tl_x, wy + br_y),
                            (wx + tl_x, wy + tl_y),
                        )

                        draw_coloured_line(
                            draw_list,
                            top_leds,
                            (wx + tl_x, wy + tl_y),
                            (wx + br_x, wy + tl_y),
                        )

        async with asyncio.TaskGroup() as tg:
            machine_task = tg.create_task(machine.run())
            await run_hello_imgui(gui)
            machine_task.cancel()


async def run_hello_imgui(gui):
    runner_params = hello_imgui.RunnerParams()
    runner_params.fps_idling.fps_idling_mode = hello_imgui.FpsIdlingMode.early_return
    runner_params.callbacks.show_gui = gui
    runner_params.app_window_params.window_geometry.size = (1000, 600)
    hello_imgui.manual_render.setup_from_runner_params(runner_params)
    imgui.create_context()
    while not hello_imgui.get_runner_params().app_shall_exit:
        hello_imgui.manual_render.render()
        await asyncio.sleep(1 / 120)
    hello_imgui.manual_render.tear_down()


@contextmanager
def init_pygame_mixer():
    pygame.mixer.init()
    try:
        yield
    finally:
        pygame.mixer.quit()


if __name__ == "__main__":
    asyncio.run(main())
