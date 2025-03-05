from contextlib import contextmanager
import pygame


@contextmanager
def init():
    pygame.mixer.init()
    try:
        yield
    finally:
        pygame.mixer.quit()
