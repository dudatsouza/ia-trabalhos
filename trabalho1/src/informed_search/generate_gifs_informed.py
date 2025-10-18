from typing import Callable
import os
from maze_generator import read_matrix_from_file
from maze_representation import Maze
from maze_problem import MazeProblem
from heuristics import h_manhattan_distance, h_euclidean_distance
from informed_search.greedy_best_first_search import greedy_best_first_search
from informed_search.greedy_best_first_search import reconstruct_path
from best_first_search import reconstruct_path
from problem import Problem

def _collect_tree_nodes(snapshots):
    nodes = set()
    for snap in snapshots:
        if snap.get('reached'):
            nodes.update(tuple(state) for state in snap['reached'])
        for key in ('reached_F', 'reached_B'):
            if key in snap:
                nodes.update(tuple(state) for state in snap[key])
    return nodes

script_dir = os.path.dirname(os.path.abspath(__file__))


def generate_gifs_informed(problem: Problem, matrix, heuristic: str = "manhattan"):
    # Collect snapshots emitted by the search
    import visualize_matrix

    snapshots = []

    def on_step(snapshot):
        # Keep the greedy snapshot structure (visualizer understands these keys)
        snapshots.append(snapshot.copy())

    heuristic_table_coordinate = {
        (x, y): problem.heuristic((x, y), problem.goal, function_h=
            h_manhattan_distance if heuristic == "manhattan" else h_euclidean_distance)
        for x in range(problem.maze.W) for y in range(problem.maze.H)
    }

    print(heuristic_table_coordinate)

    # Run the greedy search with the callback to collect snapshots
    resultGreedy = greedy_best_first_search(problem, f=lambda n: n.f, heuristic_table_coordinate=heuristic_table_coordinate, on_step=on_step)

    if resultGreedy is None:
        print('No path found')
    else:
        solution, nodes_expanded = resultGreedy
        if snapshots:
            interval_str = input('Frame interval in ms (press Enter for 100, higher = slower): ').strip()
            try:
                interval_ms = int(interval_str) if interval_str else 100
                if interval_ms <= 0:
                    raise ValueError
            except ValueError:
                print('Invalid interval, using 100ms.')
                interval_ms = 100
            # Pass the collected snapshots directly to the visualizer (no re-run)
            out_path = os.path.join(script_dir, '../..', f'visualization-greedy-bfs-{heuristic}.gif')
            print(f'Saving visualization to {out_path}')
            visualize_matrix.visualize(
                os.path.join(script_dir, '../..', 'data', 'input', 'maze.txt'),
                f=lambda n: n.g,
                interval=interval_ms,
                precompute=True,
                precomputed_snapshots=snapshots,
                final_path=reconstruct_path(solution) if solution else None,
                tree_nodes=_collect_tree_nodes(snapshots),
                final_hold_ms=5000,
                out_file=out_path,
            )
        else:
            print('No snapshots were produced for visualization.')