import asyncio
from typing import AsyncGenerator

from pygame.mixer import Sound

from nostmack_hub.led_effect import LedEffect
from nostmack_hub.gear import Gear
from nostmack_hub.led_value_calculator import LedEffectFixedCount, LedValueCalculator
from nostmack_hub.machine_state import MachineState
from nostmack_hub.sounds import Sounds
from nostmack_hub.wled import WledProtocol


EspEvents = AsyncGenerator[tuple[int, int], None]


class Machine:

    def __init__(
        self,
        *,
        esp_mapping: dict[int, Gear],
        esp_events: EspEvents,
        wled: WledProtocol,
        effect: LedEffectFixedCount,
        sounds: Sounds,
        finale: Sound,
        finale_duration: int,
    ):
        self.esp_mapping = esp_mapping
        self.esp_events = esp_events
        self.wled = wled
        self.effect = effect
        self.sounds = sounds
        self.finale = finale
        self.finale_duration = finale_duration
        self.state = MachineState()

    @property
    def gears(self):
        return list(self.esp_mapping.values())

    async def update_effects(self):
        async for esp_id, count in self.esp_events:
            if self.state.is_charged():
                continue
            if self.state.is_initial() and count != 0:
                self.state.to_charging()

            gear = self.esp_mapping.get(esp_id)
            if gear is None:
                continue
            gear.turned(count)

    async def check_discharged(self):
        while True:
            if not all(g.is_discharged() for g in self.gears):
                await asyncio.sleep(1)
                continue

            touches = [g.touched_event() for g in self.gears]
            await asyncio.sleep(5)
            any_gears_touched = any(touch.is_set() for touch in touches)
            if not any_gears_touched:
                self.state.to_initial()
                return

    async def check_charged(self):
        while not all(g.is_charged() for g in self.gears):
            await asyncio.sleep(0.1)
        self.state.to_charged()

    async def initial(self):
        await self.wled.set_preset(1)

    async def charging(self):
        await self.wled.set_live()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.wled.keep_updated(self.led_value_calculator))
            tg.create_task(self.sounds.play_sounds())

            tg.create_task(self.check_charged())
            tg.create_task(self.check_discharged())

            for gear in self.gears:
                tg.create_task(gear.discharge_task())

    @property
    def led_value_calculator(self):
        return LedValueCalculator(gears=self.gears, effect=self.effect)

    async def charged(self):
        for gear in self.gears:
            gear.reset()
        await self.wled.set_preset(2)
        self.finale.play()
        await asyncio.sleep(self.finale_duration)
        self.state.to_initial()

    async def state_tasks(self):
        while True:
            async with asyncio.TaskGroup() as tg:
                current_state = self.state.state
                print(f"Executing state {current_state}")
                match current_state:
                    case "initial":
                        tasks = tg.create_task(self.initial())
                    case "charging":
                        tasks = tg.create_task(self.charging())
                    case "charged":
                        tasks = tg.create_task(self.charged())
                await self.state.changed_event().wait()
                print(f"Cancelling state {current_state}")
                tasks.cancel()

    async def run(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.update_effects())
            tg.create_task(self.state_tasks())
