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
    total_g = meeting_child.g + other.g
    forward_node = meeting_child
    backward_node = other
    if direction == 'B':
        forward_node, backward_node = backward_node, forward_node

    while backward_node.parent is not None:
        forward_node.action = backward_node.parent
        backward_node = backward_node.parent
        forward_node = Node(state=backward_node.state, parent=forward_node, action=backward_node.action, g=forward_node.g + 1)
    # set full path-cost on the returned node for callers
    forward_node.g = total_g
    return forward_node


def proceed(
    direction: str,
    problem: Problem,
    frontier: list,
    reached: dict,
    reached_other: dict,
    f_func: Callable[[Node], float],
    expanded_nodes: int,
    on_step: Callable[[dict], None] | None = None,
) -> Optional[Node]:
    if not frontier:
        return None
    _, node = heapq.heappop(frontier)

    # emit snapshot before expansion
    if on_step:
        dir_label = 'Forward' if direction == 'F' else 'Backward'
        if direction == 'F':
            snapshot = {
                'current': node.state,
                'frontier_F': [n.state for _, n in frontier],
                'frontier_B': [],
                'reached_F': list(reached.keys()),
                'reached_B': list(reached_other.keys()),
                'event': 'pop',
                'direction': dir_label,
                'nodes_expanded': expanded_nodes,
            }
        else:
            snapshot = {
                'current': node.state,
                'frontier_F': [],
                'frontier_B': [n.state for _, n in frontier],
                'reached_F': list(reached_other.keys()),
                'reached_B': list(reached.keys()),
                'event': 'pop',
                'direction': dir_label,
                'nodes_expanded': expanded_nodes,
            }
        on_step(snapshot)

    for child in expand(problem, node):
        s = child.state
        existing = reached.get(s)
        if existing is None or child.g < existing.g:
            reached[s] = child
            heapq.heappush(frontier, (f_func(child), child))
            # emit snapshot when pushing a child
            if on_step:
                dir_label = 'Forward' if direction == 'F' else 'Backward'
                if direction == 'F':
                    snapshot = {
                        'current': child.state,
                        'frontier_F': [n.state for _, n in frontier],
                        'frontier_B': [],
                        'reached_F': list(reached.keys()),
                        'reached_B': list(reached_other.keys()),
                        'event': 'push_child',
                        'direction': dir_label,
                        'nodes_expanded': expanded_nodes,
                    }
                else:
                    snapshot = {
                        'current': child.state,
                        'frontier_F': [],
                        'frontier_B': [n.state for _, n in frontier],
                        'reached_F': list(reached_other.keys()),
                        'reached_B': list(reached.keys()),
                        'event': 'push_child',
                        'direction': dir_label,
                        'nodes_expanded': expanded_nodes,
                    }
                on_step(snapshot)

            if s in reached_other:
                # found a meeting point
                solution = join_nodes(direction, child, reached_other)
                return solution
    return None


def bidirectional_best_first_search(problem_F: Problem, f_F: Callable[[Node], float], problem_B: Problem, f_B: Callable[[Node], float], on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    node_F = Node(state=problem_F.initial, g=0.0)
    node_B = Node(state=problem_B.initial, g=0.0)

    frontier_F = []
    frontier_B = []
    heapq.heappush(frontier_F, (f_F(node_F), node_F))
    heapq.heappush(frontier_B, (f_B(node_B), node_B))

    reached_F = {node_F.state: node_F}
    reached_B = {node_B.state: node_B}

    solution = None

    expanded_nodes = 0

    while frontier_F and frontier_B:
        topF = frontier_F[0][0]
        topB = frontier_B[0][0]
        if topF < topB:
            solution = proceed('F', problem_F, frontier_F, reached_F, reached_B, f_F, expanded_nodes, on_step=on_step)
        else:
            solution = proceed('B', problem_B, frontier_B, reached_B, reached_F, f_B, expanded_nodes, on_step=on_step)

        expanded_nodes += 1
        if solution is not None:
            return solution, expanded_nodes

    return None
