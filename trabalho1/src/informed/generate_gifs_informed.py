# EXTERNAL IMPORTS
from typing import Callable
import os
import tempfile

# INTERNAL PROJECT IMPORTS
# CORE
from core.maze_representation import Maze
from core.maze_problem import MazeProblem
from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_inadmissible
from core.problem import Problem

# INFORMED SEARCH
from informed.greedy_best_first_search import greedy_best_first_search, reconstruct_path
from informed.a_star_search import a_star_table_search
import search.visualize_matrix as visualize_matrix


# COLLECTS ALL UNIQUE NODES FROM SNAPSHOTS FOR VISUALIZATION
def _collect_tree_nodes(snapshots):
    nodes = set()
    for snap in snapshots:
        if snap.get('reached'):
            nodes.update(tuple(state) for state in snap['reached'])
        for key in ('reached_F', 'reached_B'):
            if key in snap:
                nodes.update(tuple(state) for state in snap[key])
    return nodes


# GENERATES GIFS FOR INFORMED SEARCH (GREEDY OR A*) WITH SNAPSHOT COLLECTION
def generate_gifs_informed(problem: Problem, matrix, heuristic: str = "manhattan", algorithm: str = "greedy", interval_ms: int | None = 100, out_file: str | None = None):
    
    snapshots = []

    # CALLBACK TO COLLECT SNAPSHOTS DURING SEARCH
    def on_step(snapshot):
        snapshots.append(snapshot.copy())

    # BUILD HEURISTIC TABLE MATCHING MAZE COORDINATES
    heuristic_table_coordinate = {
        (r, c): problem.heuristic(
            (r, c),
            problem.goal,
            function_h=h_manhattan_distance if heuristic == "manhattan" else
                       h_euclidean_distance if heuristic == "euclidean" else
                       h_inadmissible
        )
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }

    result = None
    # RUN THE SELECTED INFORMED SEARCH ALGORITHM
    if algorithm.lower() in ("greedy", "greedy_best_first", "greedy_bfs"):
        result = greedy_best_first_search(problem, f=lambda n: n.f, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)
    elif algorithm.lower() in ("astar", "a*", "a_star"):
        result = a_star_table_search(problem, f=lambda n: n.g + n.h, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)
    else:
        print(f"Unknown algorithm '{algorithm}', supported: greedy, a_star")
        return

    if result is None:
        print('No path found')
        return None
    solution, nodes_expanded = result

    if not snapshots:
        print('No snapshots were produced for visualization.')
        return None

    # DETERMINE FRAME INTERVAL
    if interval_ms is None:
        interval_str = input('Frame interval in ms (press Enter for 100, higher = slower): ').strip()
        try:
            interval_ms = int(interval_str) if interval_str else 100
            if interval_ms <= 0:
                raise ValueError
        except ValueError:
            print('Invalid interval, using 100ms.')
            interval_ms = 100

    # DETERMINE OUTPUT FILE PATH
    if out_file:
        out_path = out_file
    else:
        alg_name = 'a_star' if algorithm.lower() in ('astar', 'a*', 'a_star') else 'greedy'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_path = os.path.join(script_dir, '../..', f'visualization-{alg_name}-{heuristic}.gif')

    # WRITE MATRIX TO TEMPORARY FILE FOR VISUALIZER
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
            tmp = tf.name
            for row in matrix:
                tf.write(''.join(row) + '\n')

        print(f'Saving visualization to {out_path}')
        visualize_matrix.visualize(
            tmp,
            f=lambda n: n.g,
            interval=interval_ms,
            precompute=True,
            precomputed_snapshots=snapshots,
            final_path=reconstruct_path(solution) if solution else None,
            tree_nodes=_collect_tree_nodes(snapshots),
            final_hold_ms=5000,
            out_file=out_path,
        )
    finally:
        # CLEANUP TEMPORARY FILE
        try:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass

    return out_path
