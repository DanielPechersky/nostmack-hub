from imgui_bundle import imgui


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
        x = (x0 + x1) / 2
        y = (y0 + y1) / 2
        r = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
        draw_list.add_circle_filled(
            (x, y),
            r,
            imgui_colour(colour),
        )


def imgui_colour(colour):
    return imgui.IM_COL32(*colour, 255)
