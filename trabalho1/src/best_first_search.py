from typing import Callable, Optional
from problem import Problem
from node import Node
import heapq

def best_first_search(problem: Problem, f: Callable[[Node], float]) -> Optional[Node]:
    start = Node(state=problem.initial, g=0.0, h=problem.heuristic(problem.initial))
    frontier = []
    heapq.heappush(frontier, (f(start), start))
    reached = {start.state: start}

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node
        for child in expand(problem, node):
            existing = reached.get(child.state)
            if existing is None or child.g < existing.g:
                reached[child.state] = child
                heapq.heappush(frontier, (f(child), child))
    return None

def expand(problem: Problem, node: Node):
    for action in problem.actions(node.state):
        s2 = problem.result(node.state, action)
        cost = node.g + problem.action_cost(node.state, action, s2)
        child = Node(state=s2, parent=node, action=action, g=cost, h=problem.heuristic(s2))
        yield child

def reconstruct_path(node: Node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))