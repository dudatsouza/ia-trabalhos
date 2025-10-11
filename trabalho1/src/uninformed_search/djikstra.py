from typing import Optional
from problem import Problem
from node import Node
from best_first_search import best_first_search

def djikstra(problem: Problem) -> Optional[Node]:
    return best_first_search(problem, f=lambda n: n.g)