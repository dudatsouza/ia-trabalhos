from typing import Optional, Tuple, Callable
from problem import Problem
from node import Node
from best_first_search import best_first_search
from measure_time_memory import measure_time_memory
from best_first_search import reconstruct_path

def compute_dijkstra(problem: Problem):
    result, elapsed_time, memory_used, current, peak = measure_time_memory(dijkstra, problem)

    if result is None:
        print("No path found")
        return
    
    goal_node, nodes_expanded = result

    if goal_node:
        path = reconstruct_path(goal_node)
        print("Path:", path)
        print("Number of nodes expanded:", nodes_expanded)
        print("Cost of path:", goal_node.g)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

def dijkstra(problem: Problem, on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    return best_first_search(problem, f=lambda n: n.g, on_step=on_step)