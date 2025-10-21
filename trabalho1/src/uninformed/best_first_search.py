# EXTERNAL IMPORTS
import heapq
from typing import Callable, Optional, Tuple

# INTERNAL PROJECT IMPORTS
# CORE
from core.problem import Problem
from core.node import Node

# SEARCH
# (NONE NEEDED FOR THIS FILE)

# FUNCTION TO PERFORM BEST-FIRST SEARCH WITH OPTIONAL SNAPSHOT CALLBACK
def best_first_search(problem: Problem, f: Callable[[Node], float], on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    start = Node(state=problem.initial, g=0.0, h=problem.heuristic(problem.initial, problem.goal))
    frontier = []
    heapq.heappush(frontier, (f(start), start))
    reached = {start.state: start}
    nodes_expanded = 0

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            # RETURN GOAL NODE AND NUMBER OF NODES EXPANDED
            return node, nodes_expanded

        for child in expand(problem, node):
            # EMIT SNAPSHOT BEFORE EXPANDING A NODE
            if on_step:
                snapshot = {
                    'current': node.state,
                    'frontier': [n.state for _, n in frontier],
                    'reached': list(reached.keys()),
                    'event': 'expand_node',
                    'nodes_expanded': nodes_expanded,
                }
                on_step(snapshot)
            existing = reached.get(child.state)
            if existing is None or child.g < existing.g:
                reached[child.state] = child
                heapq.heappush(frontier, (f(child), child))
                nodes_expanded += 1

                # EMIT SNAPSHOT WHEN PUSHING A CHILD
                if on_step:
                    snapshot = {
                        'current': child.state,
                        'frontier': [n.state for _, n in frontier],
                        'reached': list(reached.keys()),
                        'event': 'push_child',
                        'nodes_expanded': nodes_expanded,
                    }
                    on_step(snapshot)
    return None

# FUNCTION TO GENERATE CHILD NODES FROM CURRENT NODE
def expand(problem: Problem, node: Node):
    for action in problem.actions(node.state):
        s2 = problem.result(node.state, action)
        cost = node.g + problem.action_cost(node.state, action, s2)
        child = Node(state=s2, parent=node, action=action, g=cost, h=problem.heuristic(s2, problem.goal))
        yield child

# FUNCTION TO RECONSTRUCT PATH FROM GOAL NODE TO INITIAL STATE
def reconstruct_path(node: Node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))
