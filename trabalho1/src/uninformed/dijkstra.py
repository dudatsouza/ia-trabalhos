# EXTERNAL IMPORTS
from typing import Optional, Tuple, Callable

# INTERNAL PROJECT IMPORTS
# CORE
from core.problem import Problem
from core.node import Node

# SEARCH
from search.measure_time_memory import measure_time_memory

# UNINFORMED SEARCH
from uninformed.best_first_search import best_first_search, reconstruct_path

# DIJKSTRA SEARCH COMPUTATION FUNCTION
def compute_dijkstra(problem: Problem):
    # MEASURE TIME AND MEMORY FOR DIJKSTRA SEARCH
    result, elapsed_time, memory_used, current, peak = measure_time_memory(dijkstra, problem)

    # CHECK IF SEARCH RETURNED NONE
    if result is None:
        print("No path found")
        return
    
    goal_node, nodes_expanded = result

    # IF SOLUTION FOUND, PRINT DETAILS
    if goal_node:
        path = reconstruct_path(goal_node)
        print("Path:", path)
        print("Number of nodes expanded:", nodes_expanded)
        print("Cost of path:", goal_node.g)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")


# DIJKSTRA SEARCH CORE FUNCTION
def dijkstra(problem: Problem, on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    # CALL BEST-FIRST SEARCH WITH f(n) = g(n) (COST SO FAR)
    return best_first_search(problem, f=lambda n: n.g, on_step=on_step)
