from contextlib import contextmanager
import pygame


@contextmanager
def init():
    pygame.mixer.init(buffer=2048)
    try:
        pygame.mixer.set_num_channels(12)
        yield
    finally:
        pygame.mixer.quit()
