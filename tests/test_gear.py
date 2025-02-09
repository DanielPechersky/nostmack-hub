import asyncio

import pytest

from nostmack_hub.gear import Gear


@pytest.mark.looptime
async def test_gear_partially_turned_fully_discharges():
    gear = Gear(1)

    async with asyncio.TaskGroup() as tg:
        discharge_task = tg.create_task(gear.discharge_task())

        gear.turned(100)
        assert gear.value.inner == 100

        # wait for gear to be idle
        await asyncio.sleep(2)

        # the gear has started discharging
        assert 0 < gear.value.inner < 100

        await asyncio.sleep(10)

        # the gear is discharged
        assert gear.value.inner == 0

        discharge_task.cancel()


@pytest.mark.looptime
async def test_gear_fully_turned_fully_discharges():
    gear = Gear(1)

    async with asyncio.TaskGroup() as tg:
        discharge_task = tg.create_task(gear.discharge_task())

        gear.turned(255)
        assert gear.value.inner == 255

        # wait for gear to be idle
        await asyncio.sleep(2)

        # but once it's fully charged, a gear takes longer to start discharging!
        assert gear.value.is_max

        # wait a longer time
        await asyncio.sleep(30)

        # the gear starts discharging
        assert 0 < gear.value.inner < 255

        await asyncio.sleep(30)

        # the gear is discharged
        assert gear.value.inner == 0

        discharge_task.cancel()
