from heuristics import h_manhattan_distance, h_euclidean_distance
from typing import Optional, Tuple, Callable
from problem import Problem
from node import Node
from measure_time_memory import measure_time_memory
import heapq

def compute_greedy_best_first_search(problem: Problem, heuristic: str):
    # For each Coord (Position) in the maze, map to its heuristic value
    heuristic_table_coordinate = {
        (x, y): problem.heuristic((x, y), problem.goal, function_h=
            h_manhattan_distance if heuristic == "manhattan" else h_euclidean_distance)
        for x in range(problem.maze.W) for y in range(problem.maze.H)
    }

    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        greedy_best_first_search, problem, lambda n: n.h, heuristic_table_coordinate
    )

    if result is None:
        print("No path found")
        return
    
    goal_node, nodes_expanded = result

    if goal_node:
        path = reconstruct_path(goal_node)
        print("Path:", path)
        print("Number of nodes expanded:", nodes_expanded)
        print("Cost of path:", goal_node.f)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

def greedy_best_first_search(problem: Problem, f: Callable[[Node], float], heuristic_table_coordinate: dict, on_step: Callable[[dict], None] | None = None) -> Optional[Tuple[Node, int]]:
    print(heuristic_table_coordinate[problem.initial])
    start = Node(state=problem.initial, f=heuristic_table_coordinate[problem.initial], h=heuristic_table_coordinate[problem.initial])
    frontier = []
    heapq.heappush(frontier, (f(start), start))
    reached = {start.state: start}
    nodes_expanded = 0

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            # return goal node, expanded count and path cost
            return node, nodes_expanded

        for child in expand(problem, node, heuristic_table_coordinate):
            # emit snapshot before expanding a node
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
            if existing is None or child.f < existing.f:
                reached[child.state] = child
                heapq.heappush(frontier, (f(child), child))
                nodes_expanded += 1

                # emit snapshot when pushing a child
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

def expand(problem: Problem, node: Node, heuristic_table_coordinate: dict):
    for action in problem.actions(node.state):
        s2 = problem.result(node.state, action)
        cost = heuristic_table_coordinate[s2] + heuristic_table_coordinate[node.state]
        child = Node(state=s2, parent=node, action=action, h=cost, f=cost)
        yield child

def reconstruct_path(node: Node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))