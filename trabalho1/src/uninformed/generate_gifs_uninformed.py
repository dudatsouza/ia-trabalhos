import os
from pathlib import Path
from typing import List
import tempfile

# Imports corrigidos para a estrutura do projeto
from core.maze_representation import Maze
from core.maze_problem import MazeProblem
from uninformed.bidirectional_best_first_search import bidirectional_best_first_search
from uninformed.dijkstra import dijkstra
from search.best_first_search import reconstruct_path
from core.problem import Problem
from search import visualize_matrix

def _collect_tree_nodes(snapshots):
    nodes = set()
    for snap in snapshots:
        if snap.get('reached'):
            nodes.update(tuple(state) for state in snap['reached'])
        for key in ('reached_F', 'reached_B'):
            if key in snap:
                nodes.update(tuple(state) for state in snap[key])
    return nodes

def generate_gifs_uninformed(problem: Problem, matrix: List[List[str]], algorithm: str, interval_ms: int = 100, out_file: str | Path | None = None) -> str | None:
    """
    Gera um GIF para um algoritmo não informado (Dijkstra ou Bidirectional).

    Args:
        problem: O objeto MazeProblem.
        matrix: A matriz do labirinto para visualização.
        algorithm: 'dijkstra' ou 'bidirectional'.
        interval_ms: Intervalo entre frames em milissegundos.
        out_file: Caminho para salvar o GIF.

    Returns:
        O caminho do arquivo de saída se o GIF foi gerado, senão None.
    """
    
    snapshots = []
    def on_step(snapshot):
        snapshots.append(snapshot.copy())

    result = None
    if algorithm.lower() == 'dijkstra':
        result = dijkstra(problem, on_step=on_step)
    elif algorithm.lower() == 'bidirectional':
        # Prepara o problema reverso para a busca bidirecional
        matrix_2 = [row[:] for row in matrix]
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S': matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G': matrix_2[r][c] = 'S'
        problem_2 = MazeProblem(Maze(matrix_2))
        result = bidirectional_best_first_search(problem_F=problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g, on_step=on_step)
    else:
        print(f"Algoritmo desconhecido: {algorithm}")
        return None

    if result is None:
        print(f'{algorithm.capitalize()}: Nenhum caminho encontrado.')
        return None
        
    solution, _ = result
    if not snapshots:
        print(f'{algorithm.capitalize()}: Nenhum snapshot produzido para visualização.')
        return None

    # Usa um arquivo temporário para a matriz para garantir que o visualizador
    # use a matriz correta que está na memória da GUI.
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
        if tmp_maze_path and os.path.exists(tmp_maze_path):
            try:
                os.unlink(tmp_maze_path)
            except Exception: pass
            
    return str(out_file)