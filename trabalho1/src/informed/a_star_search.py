from typing import Callable, Optional, Tuple, List, Dict
import heapq

from core.problem import Problem
from core.node import Node


def a_star_table_search(problem: Problem, f: Callable[[Node], float], heuristic_table_coordinate: Dict[tuple, float], on_step: Optional[Callable[[dict], None]] = None) -> Optional[Tuple[Node, int]]:
    """A* variant that uses a precomputed heuristic table (heuristic_table_coordinate).

    This mirrors the style of greedy_best_first_search which expects a heuristic table
    passed in. The function uses g + h_table[state] as f(n).
    """
    start = Node(state=problem.initial, g=0.0, h=heuristic_table_coordinate[problem.initial], f=heuristic_table_coordinate[problem.initial])
    frontier = []
    heapq.heappush(frontier, (f(start), start))
    reached = {start.state: start}
    nodes_expanded = 0

    while frontier:
        _, node = heapq.heappop(frontier)
        if problem.is_goal(node.state):
            return node, nodes_expanded

        # mark explored
        reached_node = reached.get(node.state)
        # skip outdated entries: if reached maps to a different node with better g, skip
        if reached_node is not None and reached_node is not node and reached_node.g < node.g:
            continue

        # expand children
        for action in problem.actions(node.state):
            s2 = problem.result(node.state, action)
            g2 = node.g + problem.action_cost(node.state, action, s2)
            h_val = heuristic_table_coordinate.get(s2, 0.0)
            child = Node(state=s2, parent=node, action=action, g=g2, h=h_val, f=g2 + h_val)

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
            if existing is None or child.g < existing.g:
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


def a_star_search(problem: Problem, h: Optional[Callable[[any, any], float]] = None, on_step: Optional[Callable[[dict], None]] = None) -> Optional[Tuple[Node, int]]:
    """Public A* wrapper that builds a heuristic table and calls the table-based A*.

    Keeps the old signature (problem, h) so existing callers (GUI) remain compatible.
    If h is None, uses problem.heuristic to compute the table.
    """
    # build heuristic table similarly to greedy implementation
    heuristic_fn = h
    if heuristic_fn is None:
        # use problem.heuristic compatible signature: (s, goal, function_h=None)
        heuristic_fn = lambda s, goal: problem.heuristic(s, goal)

    heuristic_table_coordinate = {
        (x, y): heuristic_fn((x, y), problem.goal)
        for x in range(problem.maze.W) for y in range(problem.maze.H)
    }

    # define f for A*
    def f(n: Node) -> float:
        return n.g + n.h

    return a_star_table_search(problem, f=f, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)
