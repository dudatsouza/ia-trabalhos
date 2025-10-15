import psutil
import tracemalloc
import time

def measure_time_memory(func, *args, **kwargs):
    process = psutil.Process()
    
    # Measure memory before execution
    tracemalloc.start()
    before = process.memory_info().rss
    
    # Measure time before execution
    start_time = time.perf_counter()
    
    # Execute the function
    result = func(*args, **kwargs)
    
    # Measure time after execution
    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Measure memory after execution
    after = process.memory_info().rss
    memory_used = after - before
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return result, elapsed_time, memory_used, current, peak