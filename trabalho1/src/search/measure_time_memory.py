# EXTERNAL IMPORTS
import time
import tracemalloc

# OPTIONAL EXTERNAL IMPORT
try:
    import psutil
except Exception:
    psutil = None

# FUNCTION TO MEASURE RUNTIME AND MEMORY USAGE OF AN ARBITRARY FUNCTION
def measure_time_memory(func, *args, **kwargs):
    # CREATE PROCESS OBJECT FOR RSS MEASUREMENT IF PSUTIL IS AVAILABLE
    process = psutil.Process() if psutil is not None else None

    # START TRACEMALLOC TO TRACK CURRENT AND PEAK PYTHON MEMORY
    tracemalloc.start()

    # MEASURE RSS BEFORE EXECUTION
    before = process.memory_info().rss if process is not None else 0

    # MEASURE TIME BEFORE EXECUTION
    start_time = time.perf_counter()

    # EXECUTE THE FUNCTION
    result = func(*args, **kwargs)

    # MEASURE TIME AFTER EXECUTION
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # CONVERT TO MILLISECONDS

    # MEASURE RSS AFTER EXECUTION
    after = process.memory_info().rss if process is not None else 0
    memory_used = after - before

    # GET CURRENT AND PEAK PYTHON MEMORY FROM TRACEMALLOC
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # RETURN FUNCTION RESULT, ELAPSED TIME, RSS MEMORY, CURRENT AND PEAK TRACEMALLOC MEMORY
    return result, elapsed_time, memory_used, current, peak
