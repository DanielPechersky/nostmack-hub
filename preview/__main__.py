import asyncio
from contextlib import contextmanager
from pathlib import Path
import dotenv
import imgui
from imgui.integrations.pygame import PygameRenderer
import pygame
import OpenGL.GL as gl

from nostmack_hub.led_effect import SectoredEffect, StripedEffect, SteampunkChargingEffect
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


async def main():
    with init_pygame():

        size = 1000, 600

        pygame.display.set_mode(
            size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        imgui.create_context()
        impl = PygameRenderer()

        imgui.get_io().display_size = size
        imgui.get_io().ini_file_name = ""

        effects = [
            StripedEffect(COLOURS, LED_COUNT),
            SectoredEffect(COLOURS, LED_COUNT),
            SteampunkChargingEffect(COLOURS, LED_COUNT),
        ]
        selected_effect = 0

        machine, esp_events, wled = init_machine(
            effects[selected_effect], SOUND_POOL, SOUND_DING, SOUND_FINALE
        )

        gear_turns = {esp_id: 0.0 for esp_id, _ in machine.esp_mapping.items()}

        clock = pygame.time.Clock()

        async with asyncio.TaskGroup() as tg:
            machine_task = tg.create_task(machine.run())

            while True:
                dt = clock.tick() / 1000

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        machine_task.cancel()
                        return
                    impl.process_event(event)
                impl.process_inputs()

                imgui.new_frame()

                with imgui.begin("Settings"):
                    imgui.set_window_position(550, 0, imgui.FIRST_USE_EVER)

                    for i, gear in machine.esp_mapping.items():
                        imgui.text(f"Gear {i}: {gear.value.inner}")
                        imgui.button("Slow turn")
                        if imgui.is_item_hovered():
                            gear_turns[i] += dt * 10
                        imgui.same_line()
                        imgui.button("Fast turn")
                        if imgui.is_item_hovered():
                            gear_turns[i] += dt * 50

                    with imgui.begin_list_box("Effect", 150, 50) as combo:
                        if combo.opened:
                            for i, effect in enumerate(effects):
                                is_selected = i == selected_effect
                                if imgui.selectable(
                                    effect.__class__.__name__, is_selected
                                )[0]:
                                    selected_effect = i

                                # Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
                                if is_selected:
                                    imgui.set_item_default_focus()
                    imgui.text(
                        "note: machine must not be charging to change effects")

                    if imgui.button("Reset machine"):
                        machine.state.to_initial()
                        for gear in machine.gears:
                            gear.reset()

                for i, turn in gear_turns.items():
                    sensed_turns = round(turn)
                    gear_turns[i] -= sensed_turns
                    esp_events.append((i, sensed_turns))

                machine.effect = effects[selected_effect]

                with imgui.begin("Pattern"):
                    imgui.set_window_position(0, 0, imgui.FIRST_USE_EVER)
                    imgui.set_window_size(550, 550, imgui.FIRST_USE_EVER)

                    match wled.state:
                        case WledPreset(id):
                            imgui.text(f"Preset id: {id}")
                        case WledRealtime(leds):
                            draw_list = imgui.get_window_draw_list()
                            wx, wy = imgui.get_window_position()

                            side_length = round(len(leds) * 3 / 10)
                            top_length = round(len(leds) * 2 / 10)

                            right_leds = leds[:side_length]
                            bottom_leds = leds[side_length:][:top_length]
                            left_leds = leds[side_length +
                                             top_length:][:side_length]
                            top_leds = leds[side_length +
                                            top_length + side_length:]

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

                gl.glClearColor(1, 1, 1, 1)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                imgui.render()
                impl.render(imgui.get_draw_data())

                pygame.display.flip()

                await asyncio.sleep(1 / 120)


@contextmanager
def init_pygame():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
