from typing import Callable, Optional, Tuple, Dict
import heapq

from problem import Problem
from node import Node
from best_first_search import expand
from measure_time_memory import measure_time_memory
from maze_problem import MazeProblem
from maze_representation import Maze
from best_first_search import reconstruct_path

def compute_bidirectional_best_first_search(problem: Problem, matrix):
    def bid_bfs():
        matrix_2 = [row[:] for row in matrix]  
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S':
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G':
                    matrix_2[r][c] = 'S'
        mz_2 = Maze(matrix_2)
        problem_2 = MazeProblem(mz_2)
        return bidirectional_best_first_search(problem_F=problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g)

    result, elapsed_time, memory_used, current, peak = measure_time_memory(bid_bfs)
    
    if result is None:
        print("No path found")
        return

    solution, nodes_expanded = result

    if solution:
        path = reconstruct_path(solution)
        print("Path:", path)
        print("Number of nodes expanded:", nodes_expanded)
        print("Cost of path:", solution.g)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

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
            expanded_nodes += 1
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
                return solution, expanded_nodes
    return None, expanded_nodes


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
            # reference to expanded_nodes, to be incremented inside proceed
            solution, expanded_nodes = proceed('F', problem_F, frontier_F, reached_F, reached_B, f_F, expanded_nodes, on_step=on_step)
        else:
            # reference to expanded_nodes, to be incremented inside proceed
            solution, expanded_nodes = proceed('B', problem_B, frontier_B, reached_B, reached_F, f_B, expanded_nodes, on_step=on_step)

        if solution is not None:
            return solution, expanded_nodes

    return None
