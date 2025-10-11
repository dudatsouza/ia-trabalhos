from typing import Callable, Optional, Tuple, Dict
import heapq

from problem import Problem
from node import Node
from best_first_search import expand


def join_nodes(direction: str, meeting_child: Node, reached_other: Dict) -> Node:
    """Reconstruct a solution Node combining forward and backward paths.

    direction is 'F' or 'B' meaning meeting_child came from that direction.
    reached_other maps states to Node from the opposite frontier.
    Returns a new Node representing the joined path (with path-cost set).
    """
    other = reached_other[meeting_child.state]

    # Build forward path (from initial to meeting)
    # and backward path (from goal to meeting)
    # We'll attach other (which is from opposite search) to meeting_child appropriately
    if direction == 'F':
        # meeting_child is in forward search; other is from backward search
        # attach other as child of meeting_child (we need a combined node)
        # Create a new dummy node for the join with combined cost
        total_g = meeting_child.g + other.g
        join = Node(state=meeting_child.state, parent=meeting_child.parent, action=meeting_child.action, g=total_g, h=0)
        return join
    else:
        total_g = meeting_child.g + other.g
        join = Node(state=meeting_child.state, parent=other.parent, action=other.action, g=total_g, h=0)
        return join


def proceed(direction: str, problem: Problem, frontier: list, reached: dict, reached_other: dict, f_func: Callable[[Node], float]) -> Optional[Node]:
    if not frontier:
        return None
    _, node = heapq.heappop(frontier)

    for child in expand(problem, node):
        s = child.state
        existing = reached.get(s)
        if existing is None or child.g < existing.g:
            reached[s] = child
            heapq.heappush(frontier, (f_func(child), child))
            if s in reached_other:
                # found a meeting point
                solution = join_nodes(direction, child, reached_other)
                return solution
    return None


def bidirectional_best_first_search(problem_F: Problem, f_F: Callable[[Node], float], problem_B: Problem, f_B: Callable[[Node], float]) -> Optional[Node]:
    node_F = Node(state=problem_F.initial, g=0.0, h=problem_F.heuristic(problem_F.initial))
    node_B = Node(state=problem_B.initial, g=0.0, h=problem_B.heuristic(problem_B.initial))

    frontier_F = []
    frontier_B = []
    heapq.heappush(frontier_F, (f_F(node_F), node_F))
    heapq.heappush(frontier_B, (f_B(node_B), node_B))

    reached_F = {node_F.state: node_F}
    reached_B = {node_B.state: node_B}

    solution = None

    while frontier_F and frontier_B:
        topF = frontier_F[0][0]
        topB = frontier_B[0][0]
        if topF < topB:
            solution = proceed('F', problem_F, frontier_F, reached_F, reached_B, f_F)
        else:
            solution = proceed('B', problem_B, frontier_B, reached_B, reached_F, f_B)

        if solution is not None:
            return solution

    return None
