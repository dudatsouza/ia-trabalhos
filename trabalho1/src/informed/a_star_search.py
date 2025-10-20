from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
from typing import Optional, Tuple, Callable, Dict
from core.problem import Problem
from core.node import Node
from search.measure_time_memory import measure_time_memory
import heapq

def compute_a_star_search(problem: Problem, heuristic: str):
    # 1. Construir a tabela de heurística (seu código está aqui)
    heuristic_table_coordinate = {
        (x, y): problem.heuristic((x, y), problem.goal, function_h=
            h_manhattan_distance if heuristic == "manhattan" else  h_euclidean_distance if heuristic == "euclidean" else h_octile_distance if heuristic == "octile" else h_chebyshev_distance)
        for x in range(problem.maze.W) for y in range(problem.maze.H)
    }

    # 2. Definir a função f CORRETA para A*
    f_astar = lambda n: n.g + n.h 

    # 3. Chamar 'a_star_table_search' (NÃO 'a_star_search')
    # A assinatura de a_star_table_search é: (problem, f, heuristic_table_coordinate, on_step)
    # Nós omitimos 'on_step' (passando None)
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        a_star_table_search,      # <--- MUDANÇA AQUI
        problem,
        f_astar,                  # <--- MUDANÇA AQUI (g + h)
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
        # 4. Corrigir o Custo: O custo real é 'g', não 'f'
        print("Cost of path:", goal_node.g) # <--- MUDANÇA AQUI
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")


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
        (r, c): heuristic_fn((r, c), problem.goal)
        for r in range(problem.maze.H) for c in range(problem.maze.W) #
    }

    # define f for A*
    def f(n: Node) -> float:
        return n.g + n.h

    return a_star_table_search(problem, f=f, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)

def expand(problem: Problem, node: Node, heuristic_table_coordinate: dict):
    for action in problem.actions(node.state):
        s2 = problem.result(node.state, action)
        cost = heuristic_table_coordinate[s2]
        child = Node(state=s2, parent=node, action=action, h=cost, f=cost)
        yield child

def reconstruct_path(node: Node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))