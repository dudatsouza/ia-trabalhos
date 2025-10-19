"""Measure runtime and (approx) memory used by calling a function.

This helper prefers psutil when available to measure RSS before/after
the call. If psutil is not installed in the environment we fall back to
using tracemalloc to report the current and peak Python memory allocations
and report RSS-based memory as 0.

Returns: result, elapsed_time_ms, memory_used_bytes, current_tracemalloc, peak_tracemalloc
"""
try:
    import psutil
except Exception:
    psutil = None

import tracemalloc
import time


def measure_time_memory(func, *args, **kwargs):
    # Optional process RSS measurement
    process = psutil.Process() if psutil is not None else None

    # Measure memory before execution
    tracemalloc.start()
    before = process.memory_info().rss if process is not None else 0

    # Measure time before execution
    start_time = time.perf_counter()

    # Execute the function
    result = func(*args, **kwargs)

    # Measure time after execution
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

    # Measure memory after execution
    after = process.memory_info().rss if process is not None else 0
    memory_used = after - before
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return result, elapsed_time, memory_used, current, peak
