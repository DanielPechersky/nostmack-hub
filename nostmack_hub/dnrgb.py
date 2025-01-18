import struct
from typing import Iterable
import itertools


def dnrgb_packets(rgb_values: list[tuple[int, int, int]]):
    MAX_SIZE = 489

    for i in range(0, len(rgb_values), MAX_SIZE):
        yield dnrgb_packet(rgb_values[i : i + MAX_SIZE], start_index=i)


def dnrgb_packet(rgb_values: Iterable[tuple[int, int, int]], *, start_index) -> bytes:
    rgb_bytes = bytes(itertools.chain.from_iterable(rgb_values))

    return dnrgb_header(5, start_index) + rgb_bytes


def dnrgb_header(wait_time: int, start_index: int) -> bytes:
    DNRGB_PROTOCOL_VALUE = 4

    if wait_time > 255:
        raise ValueError("Wait time must be within 0-255")
    if start_index > 2**16 - 1:
        raise ValueError("Start index must be a nonnegative 16-bit number")
    return struct.pack(">BBH", DNRGB_PROTOCOL_VALUE, wait_time, start_index)
