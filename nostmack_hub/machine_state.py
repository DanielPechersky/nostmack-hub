import asyncio
from typing import Literal


class MachineState:
    def __init__(self):
        self.state: Literal["initial", "charging", "charged"] = "initial"
        self._changed_event = asyncio.Event()

    def _on_change(self):
        self._changed_event.set()
        self._changed_event = asyncio.Event()

    def changed_event(self):
        return self._changed_event

    def to_initial(self):
        if self.is_initial():
            return
        self.state = "initial"
        self._on_change()

    def is_initial(self):
        return self.state == "initial"

    def to_charging(self):
        if self.is_charging():
            return
        self.state = "charging"
        self._on_change()

    def is_charging(self):
        return self.state == "charging"

    def to_charged(self):
        if self.is_charged():
            return
        self.state = "charged"
        self._on_change()

    def is_charged(self):
        return self.state == "charged"
