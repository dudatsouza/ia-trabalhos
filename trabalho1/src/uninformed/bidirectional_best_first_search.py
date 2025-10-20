# EXTERNAL IMPORTS
from typing import Callable, Optional, Tuple, Dict
import heapq

# INTERNAL PROJECT IMPORTS
# CORE
from core.problem import Problem
from core.node import Node
from core.maze_problem import MazeProblem
from core.maze_representation import Maze

# SEARCH
from search.best_first_search import expand, reconstruct_path
from search.measure_time_memory import measure_time_memory


# BIDIRECTIONAL BEST-FIRST SEARCH COMPUTATION FUNCTION
def compute_bidirectional_best_first_search(problem: Problem, matrix):
    # FUNCTION TO RUN BIDIRECTIONAL BEST-FIRST SEARCH WITH MATRIX REVERSAL
    def bid_bfs():
        # COPY MATRIX TO AVOID MODIFYING ORIGINAL
        matrix_2 = [row[:] for row in matrix]  
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                # SWAP START AND GOAL FOR BACKWARD SEARCH
                if matrix_2[r][c] == 'S':
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G':
                    matrix_2[r][c] = 'S'
        mz_2 = Maze(matrix_2)
        problem_2 = MazeProblem(mz_2)
        return bidirectional_best_first_search(
            problem_F=problem, 
            f_F=lambda n: n.g, 
            problem_B=problem_2, 
            f_B=lambda n: n.g
        )

    # MEASURE TIME AND MEMORY USAGE OF THE SEARCH
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


# FUNCTION TO JOIN NODES FROM FORWARD AND BACKWARD SEARCH
def join_nodes(direction: str, meeting_child: Node, reached_other: Dict) -> Node:
    # RECONSTRUCT SOLUTION NODE COMBINING FORWARD AND BACKWARD PATHS
    other = reached_other[meeting_child.state]

    # SET TOTAL PATH-COST
    total_g = meeting_child.g + other.g
    forward_node = meeting_child
    backward_node = other
    if direction == 'B':
        # SWAP NODES IF DIRECTION IS BACKWARD
        forward_node, backward_node = backward_node, forward_node

    # ATTACH BACKWARD PATH TO FORWARD NODE
    while backward_node.parent is not None:
        forward_node.action = backward_node.parent
        backward_node = backward_node.parent
        forward_node = Node(
            state=backward_node.state, 
            parent=forward_node, 
            action=backward_node.action, 
            g=forward_node.g + 1
        )

    forward_node.g = total_g
    return forward_node


# PROCEED FUNCTION TO EXPAND ONE NODE IN BIDIRECTIONAL SEARCH
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
    # RETURN NONE IF FRONTIER IS EMPTY
    if not frontier:
        return None

    # POP NODE FROM HEAP FRONTIER
    _, node = heapq.heappop(frontier)

    # EMIT SNAPSHOT BEFORE EXPANSION IF CALLBACK EXISTS
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

    # EXPAND CHILDREN
    for child in expand(problem, node):
        s = child.state
        existing = reached.get(s)
        if existing is None or child.g < existing.g:
            # ADD CHILD TO REACHED AND FRONTIER
            reached[s] = child
            heapq.heappush(frontier, (f_func(child), child))
            expanded_nodes += 1

            # EMIT SNAPSHOT AFTER PUSHING CHILD
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

            # CHECK IF MEETING POINT FOUND
            if s in reached_other:
                solution = join_nodes(direction, child, reached_other)
                return solution, expanded_nodes

    return None, expanded_nodes


# MAIN BIDIRECTIONAL BEST-FIRST SEARCH FUNCTION
def bidirectional_best_first_search(
    problem_F: Problem, 
    f_F: Callable[[Node], float], 
    problem_B: Problem, 
    f_B: Callable[[Node], float], 
    on_step: Callable[[dict], None] | None = None
) -> Optional[Tuple[Node, int]]:
    # INITIALIZE START NODES
    node_F = Node(state=problem_F.initial, g=0.0)
    node_B = Node(state=problem_B.initial, g=0.0)

    # INITIALIZE FRONTIERS
    frontier_F = []
    frontier_B = []
    heapq.heappush(frontier_F, (f_F(node_F), node_F))
    heapq.heappush(frontier_B, (f_B(node_B), node_B))

    # INITIALIZE REACHED SETS
    reached_F = {node_F.state: node_F}
    reached_B = {node_B.state: node_B}

    solution = None
    expanded_nodes = 0

    # MAIN LOOP: EXPAND FRONTIERS UNTIL SOLUTION FOUND OR EMPTY
    while frontier_F and frontier_B:
        topF = frontier_F[0][0]
        topB = frontier_B[0][0]

        if topF < topB:
            # EXPAND FORWARD FRONTIER
            solution, expanded_nodes = proceed(
                'F', problem_F, frontier_F, reached_F, reached_B, f_F, expanded_nodes, on_step=on_step
            )
        else:
            # EXPAND BACKWARD FRONTIER
            solution, expanded_nodes = proceed(
                'B', problem_B, frontier_B, reached_B, reached_F, f_B, expanded_nodes, on_step=on_step
            )

        if solution is not None:
            return solution, expanded_nodes

    return None
