from typing import Protocol


class Effect[T](Protocol):
    def get(self) -> T:
        raise NotImplementedError

    def update(self, counts: int):
        raise NotImplementedError


class BrightnessEffect(Effect):
    def __init__(self, sensitivity):
        self.value = 0
        self.sensitivity = sensitivity

    def get(self):
        return boomerang(self.value)

    def update(self, counts):
        self.value += counts * self.sensitivity
        self.value %= 512


class EffectIntensityEffect(Effect):
    def __init__(self, sensitivity):
        self.value = 0
        self.sensitivity = sensitivity

    def get(self):
        return boomerang(self.value)

    def update(self, counts):
        self.value += counts * self.sensitivity
        self.value %= 512


def boomerang(value: int) -> int:
    if value < 256:
        return value
    else:
        return 512 - 1 - value
