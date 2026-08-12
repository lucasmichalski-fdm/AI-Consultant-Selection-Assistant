"""Timing helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class DurationMs:
    value: int = 0


@contextmanager
def measure_ms() -> DurationMs:
    holder = DurationMs(0)
    start = time.perf_counter()
    try:
        yield holder
    finally:
        holder.value = int((time.perf_counter() - start) * 1000)
