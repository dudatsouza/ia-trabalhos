# EXTERNAL IMPORTS
import os
from pathlib import Path
from typing import List
import tempfile

# INTERNAL PROJECT IMPORTS
# CORE
from core.maze_representation import Maze
from core.maze_problem import MazeProblem
from core.problem import Problem

# UNINFORMED SEARCH
from uninformed.bidirectional_best_first_search import bidirectional_best_first_search
from uninformed.dijkstra import dijkstra

# SEARCH
from search.best_first_search import reconstruct_path
from search import visualize_matrix


# COLLECT ALL NODES FROM SNAPSHOTS FOR VISUALIZATION
def _collect_tree_nodes(snapshots):
    nodes = set()
    for snap in snapshots:
        if snap.get('reached'):
            nodes.update(tuple(state) for state in snap['reached'])
        for key in ('reached_F', 'reached_B'):
            if key in snap:
                nodes.update(tuple(state) for state in snap[key])
    return nodes


# GENERATE GIF FOR UNINFORMED SEARCH ALGORITHMS (DIJKSTRA OR BIDIRECTIONAL)
def generate_gifs_uninformed(
    problem: Problem,
    matrix: List[List[str]],
    algorithm: str,
    interval_ms: int = 100,
    out_file: str | Path | None = None
) -> str | None:
    # COLLECT SNAPSHOTS DURING SEARCH
    snapshots = []

    def on_step(snapshot):
        snapshots.append(snapshot.copy())

    result = None
    if algorithm.lower() == 'dijkstra':
        # RUN DIJKSTRA AND RECORD SNAPSHOTS
        result = dijkstra(problem, on_step=on_step)

    elif algorithm.lower() == 'bidirectional':
        # PREPARE REVERSED MAZE FOR BIDIRECTIONAL SEARCH
        matrix_2 = [row[:] for row in matrix]
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S': 
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G': 
                    matrix_2[r][c] = 'S'
        problem_2 = MazeProblem(Maze(matrix_2))
        # RUN BIDIRECTIONAL BEST-FIRST SEARCH AND RECORD SNAPSHOTS
        result = bidirectional_best_first_search(
            problem_F=problem,
            f_F=lambda n: n.g,
            problem_B=problem_2,
            f_B=lambda n: n.g,
            on_step=on_step
        )
    else:
        print(f"Algoritmo desconhecido: {algorithm}")
        return None

    # CHECK IF SEARCH FOUND ANY PATH
    if result is None:
        print(f'{algorithm.capitalize()}: Nenhum caminho encontrado.')
        return None
        
    solution, _ = result

    # CHECK IF ANY SNAPSHOTS WERE PRODUCED
    if not snapshots:
        print(f'{algorithm.capitalize()}: Nenhum snapshot produzido para visualização.')
        return None

    # USE TEMPORARY FILE TO STORE MAZE FOR VISUALIZATION
    tmp_maze_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tf:
            tmp_maze_path = tf.name
            for row in matrix:
                tf.write(''.join(row) + '\n')

        print(f'Salvando visualização para {out_file}')
        visualize_matrix.visualize(
            tmp_maze_path,
            f=lambda n: n.g,
            interval=interval_ms,
            precompute=True,
            precomputed_snapshots=snapshots,
            final_path=reconstruct_path(solution) if solution else None,
            tree_nodes=_collect_tree_nodes(snapshots),
            final_hold_ms=5000,
            out_file=str(out_file),
        )
    finally:
        # REMOVE TEMPORARY FILE AFTER VISUALIZATION
        if tmp_maze_path and os.path.exists(tmp_maze_path):
            try:
                os.unlink(tmp_maze_path)
            except Exception:
                pass
            
    return str(out_file)
