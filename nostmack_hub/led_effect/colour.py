Colour = tuple[int, int, int]


def add_colours(a: Colour, b: Colour) -> Colour:
    return map_colour((a[0] + b[0], a[1] + b[1], a[2] + b[2]), lambda c: min(c, 255))


def subtract_colours(a: Colour, b: Colour) -> Colour:
    return map_colour((a[0] - b[0], a[1] - b[1], a[2] - b[2]), lambda c: max(c, 0))


def scale_colour(colour, intensity):
    return map_colour(colour, lambda channel: round(channel * intensity))


def map_colour(colour: Colour, f) -> Colour:
    return (f(colour[0]), f(colour[1]), f(colour[2]))
