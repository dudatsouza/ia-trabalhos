from typing import Callable
import os
from ..core.maze_generator import read_matrix_from_file
from ..core.maze_representation import Maze
from ..core.maze_problem import MazeProblem
from .bidirectional_best_first_search import bidirectional_best_first_search
from .dijkstra import dijkstra
from ..search.best_first_search import reconstruct_path
from ..core.problem import Problem

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

def generate_gifs_uninformed(problem: Problem, matrix):
    # Prepare backward problem by swapping S and G
    matrix_2 = [row[:] for row in matrix]
    for r in range(len(matrix_2)):
        for c in range(len(matrix_2[0])):
            if matrix_2[r][c] == 'S':
                matrix_2[r][c] = 'G'
            elif matrix_2[r][c] == 'G':
                matrix_2[r][c] = 'S'
    mz_2 = Maze(matrix_2)
    problem_2 = MazeProblem(mz_2)

    # Collect snapshots emitted by the search
    from ..search import visualize_matrix

    snapshots = []

    def on_step(snapshot):
        # Keep the bidirectional snapshot structure (visualizer understands these keys)
        snapshots.append(snapshot.copy())

    # Run the bidirectional search with the callback to collect snapshots
    resultBid = bidirectional_best_first_search(problem_F=problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g, on_step=on_step)
    
    if resultBid is None:
        print('No path found')
    else:
        solution, nodes_expanded = resultBid
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
            out_path = os.path.join(script_dir, '../..', 'visualization-bid-bfs.gif')
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
    # Visualize Dijkstra's search
    snapshots = []

    # Run dijkstra to get the solution path
    resultDijkstra = dijkstra(problem, on_step=on_step)

    if resultDijkstra is None:
        print('No path found')
    else:
        solution, nodes_expanded = resultDijkstra
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
            out_path = os.path.join(script_dir, '../..', 'visualization-dijkstra.gif')
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
