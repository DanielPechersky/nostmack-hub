from contextlib import asynccontextmanager
import asyncio_dgram


@asynccontextmanager
async def connect(addr):
    socket = await asyncio_dgram.connect(addr)
    try:
        yield socket
    finally:
        socket.close()


@asynccontextmanager
async def bind(addr):
    socket = await asyncio_dgram.bind(addr)
    try:
        yield socket
    finally:
        socket.close()
