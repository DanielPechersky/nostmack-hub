from dataclasses import dataclass
from typing import Protocol


class Animation(Protocol):
    @property
    def total_time(self) -> int:
        raise NotImplementedError

    def value(self, progress: int) -> float:
        raise NotImplementedError


class AnimatedValue:
    def __init__(self, animation: Animation, progress: int = 0):
        self.animation = animation
        self._progress = progress

    @property
    def finished_animating(self) -> bool:
        return self._progress > self.animation.total_time

    def tick(self, delta):
        if not self.finished_animating:
            self._progress += delta

    def value(self) -> float:
        return self.animation.value(self._progress)


@dataclass
class Ramp(Animation):
    time: int

    @property
    def total_time(self):
        return self.time

    def value(self, progress):
        if progress > self.time:
            return 0
        return progress / self.time


@dataclass
class Hold(Animation):
    time: int

    @property
    def total_time(self):
        return self.time

    def value(self, progress):
        if progress > self.time:
            return 0
        return 1


@dataclass
class Dissapate(Animation):
    time: int

    @property
    def total_time(self):
        return self.time

    def value(self, progress):
        if progress > self.time:
            return 0

        return max(self.time - progress, 0) / self.time


@dataclass
class Animations(Animation):
    animations: list[Animation]

    @property
    def total_time(self):
        return sum(a.total_time for a in self.animations)

    def value(self, progress):
        for animation in self.animations:
            if progress <= animation.total_time:
                return animation.value(progress)

            progress -= animation.total_time
        return 0
