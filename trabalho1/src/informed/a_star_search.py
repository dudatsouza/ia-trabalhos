# EXTERNAL IMPORTS
import heapq
from typing import Optional, Tuple, Callable, Dict, Any

# INTERNAL PROJECT IMPORTS
# CORE
from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_inadmissible
from core.problem import Problem
from core.node import Node

# SEARCH
from search.measure_time_memory import measure_time_memory


# COMPUTES A* SEARCH USING A SPECIFIED HEURISTIC
def compute_a_star_search(problem: Problem, heuristic: str):
    # BUILD HEURISTIC TABLE FOR ALL COORDINATES
    heuristic_table_coordinate = {
        (x, y): problem.heuristic(
            (x, y),
            problem.goal,
            function_h=h_manhattan_distance if heuristic == "manhattan" else
                       h_euclidean_distance if heuristic == "euclidean" else
                       h_inadmissible
                       
        )
        for x in range(problem.maze.W) for y in range(problem.maze.H)
    }

    # DEFINE f FUNCTION FOR A* (G + H)
    f_astar = lambda n: n.g + n.h 

    # CALL THE TABLE-BASED A* SEARCH AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        a_star_table_search,
        problem,
        f_astar,
        heuristic_table_coordinate
    )

    if result is None:
        print("No path found")
        return
    
    goal_node, nodes_expanded = result

    if goal_node:
        path = reconstruct_path(goal_node)
        print("Path:", path)
        print("Number of nodes expanded:", nodes_expanded)
        print("Cost of path:", goal_node.g)  # REAL COST IS G, NOT F
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")


# A* SEARCH USING PRECOMPUTED HEURISTIC TABLE
def a_star_table_search(problem: Problem, f: Callable[[Node], float],
                        heuristic_table_coordinate: Dict[tuple, float],
                        on_step: Optional[Callable[[dict], None]] = None) -> Optional[Tuple[Node, int]]:
    start = Node(
        state=problem.initial,
        g=0.0,
        h=heuristic_table_coordinate[problem.initial],
        f=heuristic_table_coordinate[problem.initial]
    )
    frontier = []
    heapq.heappush(frontier, (f(start), start))
    explored = {}
    nodes_expanded = 0

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node, nodes_expanded

        reached_node = explored.get(node.state)
        if reached_node is not None and reached_node is not node and reached_node.g < node.g:
            continue

        # EXPAND CHILDREN
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            g2 = node.g + problem.action_cost(node.state, action, s2)
            h_val = heuristic_table_coordinate.get(s2, 0.0)
            child = Node(state=s2, parent=node, action=action, g=g2, h=h_val, f=g2 + h_val)

            if on_step:
                snapshot = {
                    'current': node.state,
                    'frontier': [n.state for _, n in frontier],
                    'reached': list(explored.keys()),
                    'event': 'expand_node',
                    'nodes_expanded': nodes_expanded,
                }
                on_step(snapshot)

            existing = explored.get(child.state)
            if existing is None or child.g < existing.g:
                explored[child.state] = child
                heapq.heappush(frontier, (f(child), child))
                nodes_expanded += 1

                if on_step:
                    snapshot = {
                        'current': child.state,
                        'frontier': [n.state for _, n in frontier],
                        'reached': list(explored.keys()),
                        'event': 'push_child',
                        'nodes_expanded': nodes_expanded,
                    }
                    on_step(snapshot)
    return None


# PUBLIC WRAPPER FOR A* THAT BUILDS HEURISTIC TABLE
def a_star_search(problem: Problem, h: Optional[Callable[[Any, Any], float]] = None,
                  on_step: Optional[Callable[[dict], None]] = None) -> Optional[Tuple[Node, int]]:
    heuristic_fn = h or (lambda s, goal: problem.heuristic(s, goal))

    heuristic_table_coordinate = {
        (r, c): heuristic_fn((r, c), problem.goal)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }

    # DEFINE f FOR A* (G + H)
    def f(n: Node) -> float:
        return n.g + n.h

    return a_star_table_search(problem, f=f, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)

# RECONSTRUCTS THE PATH FROM GOAL NODE TO START NODE
def reconstruct_path(node: Node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))
