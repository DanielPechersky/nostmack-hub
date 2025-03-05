from contextlib import contextmanager
import pygame


@contextmanager
def init():
    pygame.mixer.init()
    try:
        pygame.mixer.set_num_channels(12)
        yield
    finally:
        pygame.mixer.quit()
