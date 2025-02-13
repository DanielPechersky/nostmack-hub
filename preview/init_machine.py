import asyncio
from pathlib import Path
from pygame.mixer import Sound

from nostmack_hub.gear import Gear
from nostmack_hub.machine import Machine
from nostmack_hub.sounds import Sounds
from preview.wled_mock import WledMock


def init_machine(effect, sound_pool: Path, sound_ding: Path, sound_finale: Path):
    esp_events: list[tuple[int, int]] = []

    async def mock_esp_listener():
        while True:
            for event in esp_events:
                yield event
            esp_events.clear()
            await asyncio.sleep(1 / 120)

    wled = WledMock()

    esp_mapping = {
        0: Gear(5),
        1: Gear(5),
        2: Gear(5),
        3: Gear(5),
        4: Gear(5),
    }
    sounds = list(map(Sound, Path(sound_pool).iterdir()))
    sounds = Sounds(
        gears=list(esp_mapping.values()),
        sounds=sounds,
        ding=Sound(sound_ding),
    )
    machine = Machine(
        esp_mapping=esp_mapping,
        esp_events=mock_esp_listener(),
        wled=wled,
        effect=effect,
        sounds=sounds,
        finale=Sound(sound_finale),
    )

    return machine, esp_events, wled
