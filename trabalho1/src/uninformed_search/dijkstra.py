from typing import Optional, Tuple, Callable
from problem import Problem
from node import Node
from best_first_search import best_first_search

def dijkstra(problem: Problem, on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    return best_first_search(problem, f=lambda n: n.g, on_step=on_step)