import asyncio


async def cancel_on_signal(coro):
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(coro)
        await quit_signal_event().wait()
        task.cancel()


def quit_signal_event():
    from signal import SIGINT, SIGTERM

    event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, event.set)
    return event
