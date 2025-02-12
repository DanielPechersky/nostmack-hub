from contextlib import contextmanager
import imgui
from imgui.integrations.pygame import PygameRenderer
import pygame
import OpenGL.GL as gl

from nostmack_hub.led_effect import SectoredEffect, StripedEffect

COLOURS = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]


def main():
    with init_pygame():

        size = 800, 600

        pygame.display.set_mode(
            size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        imgui.create_context()
        impl = PygameRenderer()

        imgui.get_io().display_size = size
        imgui.get_io().ini_file_name = ""

        gears = [0] * 5

        effects = [StripedEffect(COLOURS, 840), SectoredEffect(COLOURS, 840)]
        selected_effect = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                impl.process_event(event)
            impl.process_inputs()

            imgui.new_frame()

            with imgui.begin("Settings"):
                imgui.set_window_position(550, 0, imgui.FIRST_USE_EVER)

                for i, gear in enumerate(gears):
                    changed, value = imgui.slider_int(f"Gear {i}", gear, 0, 255)
                    gears[i] = value

                with imgui.begin_list_box("Effect", 150, 50) as combo:
                    if combo.opened:
                        for i, effect in enumerate(effects):
                            is_selected = i == selected_effect
                            if imgui.selectable(effect.__class__.__name__, is_selected)[
                                0
                            ]:
                                selected_effect = i

                            # Set the initial focus when opening the combo (scrolling + keyboard navigation focus)
                            if is_selected:
                                imgui.set_item_default_focus()

            effect = effects[selected_effect]

            leds = effect.calculate(gears)

            with imgui.begin("Pattern"):
                imgui.set_window_position(0, 0, imgui.FIRST_USE_EVER)
                imgui.set_window_size(550, 550, imgui.FIRST_USE_EVER)

                draw_list = imgui.get_window_draw_list()
                wx, wy = imgui.get_window_position()

                # step = len(leds) ** -1
                # for i, led in enumerate(leds):
                #     pos = i * step
                #     p0 = arc(500, 1000, 500, pos)
                #     p1 = arc(500, 1000, 500, pos + step)
                #     draw_list.add_line(*p0, *p1, imgui.get_color_u32_rgba(*led, 0))
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

            gl.glClearColor(1, 1, 1, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            impl.render(imgui.get_draw_data())

            pygame.display.flip()


def draw_coloured_line(draw_list, colours, p0, p1):
    x0, y0 = p0
    x1, y1 = p1

    x_step = (x1 - x0) / len(colours)
    y_step = (y1 - y0) / len(colours)

    draw_coloured_path(
        draw_list,
        colours,
        (
            (
                (
                    x0 + i * x_step,
                    y0 + i * y_step,
                ),
                (
                    x0 + (i + 1) * x_step,
                    y0 + (i + 1) * y_step,
                ),
            )
            for i in range(len(colours))
        ),
    )


def draw_coloured_path(draw_list, colours, points):
    for colour, ((x0, y0), (x1, y1)) in zip(colours, points, strict=True):
        draw_list.add_line(
            x0,
            y0,
            x1,
            y1,
            imgui_colour(colour),
            thickness=3,
        )


def imgui_colour(colour):
    return imgui.get_color_u32_rgba(*(channel / 255 for channel in colour), 1)


@contextmanager
def init_pygame():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
