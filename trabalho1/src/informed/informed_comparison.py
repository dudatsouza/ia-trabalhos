# EXTERNAL IMPORTS
import statistics
import sys
from pathlib import Path
from typing import Dict, Any, Callable, List

# INTERNAL PROJECT IMPORTS
# CORE
from core.maze_representation import Maze
from core.maze_problem import MazeProblem
from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
from core.node import Node

# INFORMED SEARCH
from informed.a_star_search import a_star_table_search 
from informed.greedy_best_first_search import greedy_best_first_search, reconstruct_path

# SEARCH 
from search.measure_time_memory import measure_time_memory


def compare_informed_search_algorithms(matrix: List[List[str]], num_runs: int = 15) -> Dict[str, str]:
    # CREATE A PROBLEM INSTANCE FROM THE MAZE MATRIX
    problem = MazeProblem(Maze(matrix))
    
    # DEFINE KEYS FOR ALL ALGORITHM-HEURISTIC COMBINATIONS
    keys_to_test = [
        'A*-Manhattan', 'A*-Euclidean', 'A*-Octile', 'A*-Chebyshev',
        'Greedy-Manhattan', 'Greedy-Euclidean', 'Greedy-Octile', 'Greedy-Chebyshev'
    ]
    
    # INITIALIZE METRIC STORAGE
    times: Dict[str, list] = {k: [] for k in keys_to_test}
    nodes: Dict[str, list] = {k: [] for k in keys_to_test}
    costs: Dict[str, list] = {k: [] for k in keys_to_test}
    peaks: Dict[str, list] = {k: [] for k in keys_to_test}
    found: Dict[str, int] = {k: 0 for k in keys_to_test}
    memories: Dict[str, list] = {k: [] for k in keys_to_test}
    currents: Dict[str, list] = {k: [] for k in keys_to_test}

    # PRECOMPUTE HEURISTIC TABLES FOR ALL HEURISTICS
    heuristic_table_manh = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_manhattan_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    heuristic_table_euc = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_euclidean_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    heuristic_table_oct = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_octile_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    heuristic_table_cheby = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_chebyshev_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
        
    # DEFINE COST FUNCTIONS FOR A* AND GREEDY
    f_astar: Callable[[Node], float] = lambda n: n.g + n.h
    f_greedy: Callable[[Node], float] = lambda n: n.h

    # RUN EACH ALGORITHM FOR NUM_RUNS ITERATIONS
    for _ in range(num_runs):
        # --- A* SEARCHES ---
        for name, table in zip(
            ['A*-Manhattan','A*-Euclidean','A*-Octile','A*-Chebyshev'],
            [heuristic_table_manh, heuristic_table_euc, heuristic_table_oct, heuristic_table_cheby]
        ):
            res, t, m, c, p = measure_time_memory(a_star_table_search, problem, f_astar, table)
            if res:
                sol, ne = res
                found[name] += 1
                times[name].append(t)
                nodes[name].append(ne)
                costs[name].append(sol.g)
                peaks[name].append(p)
                memories[name].append(m)
                currents[name].append(c)

        # --- GREEDY SEARCHES ---
        for name, table in zip(
            ['Greedy-Manhattan','Greedy-Euclidean','Greedy-Octile','Greedy-Chebyshev'],
            [heuristic_table_manh, heuristic_table_euc, heuristic_table_oct, heuristic_table_cheby]
        ):
            res, t, m, c, p = measure_time_memory(greedy_best_first_search, problem, f_greedy, table)
            if res:
                sol, ne = res
                found[name] += 1
                times[name].append(t)
                nodes[name].append(ne)
                path = reconstruct_path(sol)
                costs[name].append(len(path) - 1 if path else 0)
                peaks[name].append(p)
                memories[name].append(m)
                currents[name].append(c)

    # COMPUTE AVERAGES AND ASSEMBLE FINAL METRICS DICTIONARY
    metrics = {}
    for key in times:
        avg_time = statistics.mean(times[key]) if times[key] else 0
        avg_nodes = statistics.mean(nodes[key]) if nodes[key] else 0
        avg_cost = statistics.mean(costs[key]) if costs[key] else 0
        avg_peak = statistics.mean(peaks[key]) if peaks[key] else 0
        avg_memory = statistics.mean(memories[key]) if memories[key] else 0
        avg_current = statistics.mean(currents[key]) if currents[key] else 0
        
        metrics[f'{key} avg time (ms)'] = f"{avg_time:.3f}"
        metrics[f'{key} avg nodes'] = f"{avg_nodes:.1f}"
        metrics[f'{key} avg cost'] = f"{avg_cost:.1f}"
        metrics[f'{key} avg peak (KB)'] = f"{(avg_peak / 1024):.3f}"
        metrics[f'{key} found count'] = f"{found[key]}/{num_runs}"
        metrics[f'{key} avg memory (B)'] = f"{avg_memory:.3f}"
        metrics[f'{key} avg current (KB)'] = f"{(avg_current / 1024):.3f}"
    
    return metrics
