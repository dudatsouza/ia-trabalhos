import statistics
import sys
from pathlib import Path
from typing import Dict, Any, Callable, List

# --- Adicionado para corrigir imports ---
try:
    script_dir = Path(__file__).parent.resolve()
    src_dir = script_dir.parent  # /src
    sys.path.append(str(src_dir))
except NameError:
    pass # Fallback

# --- 1. Imports Modificados ---
try:
    from core.maze_representation import Maze
    from core.maze_problem import MazeProblem
    from search.measure_time_memory import measure_time_memory
    # Importa as 4 heurísticas
    from core.heuristics import (
        h_manhattan_distance, 
        h_euclidean_distance, 
        h_octile_distance, 
        h_chebyshev_distance
    )
    from informed.a_star_search import a_star_table_search 
    from informed.greedy_best_first_search import greedy_best_first_search, reconstruct_path
    from core.node import Node
except ImportError as e:
    print(f"Erro de importação em informed_comparison.py: {e}")
    sys.exit(1)


def compare_informed_search_algorithms(matrix: List[List[str]], num_runs: int = 15) -> Dict[str, str]:
    """
    Executa a comparação entre A* e Greedy com quatro heurísticas.
    Retorna um dicionário de métricas formatado para a GUI.
    """
    
    problem = MazeProblem(Maze(matrix))
    
    # --- 2. Dicionários de Métricas Expandidos ---
    # Agora inclui Octile e Chebyshev
    keys_to_test = [
        'A*-Manhattan', 'A*-Euclidean', 'A*-Octile', 'A*-Chebyshev',
        'Greedy-Manhattan', 'Greedy-Euclidean', 'Greedy-Octile', 'Greedy-Chebyshev'
    ]
    
    times: Dict[str, list] = { k: [] for k in keys_to_test }
    nodes: Dict[str, list] = { k: [] for k in keys_to_test }
    costs: Dict[str, list] = { k: [] for k in keys_to_test }
    peaks: Dict[str, list] = { k: [] for k in keys_to_test }
    found: Dict[str, int] = { k: 0 for k in keys_to_test }

    # --- 3. Pré-cálculo das 4 Tabelas de Heurística ---
    heuristic_table_manh = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_manhattan_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    heuristic_table_euc = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_euclidean_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    # Adicionadas as novas tabelas
    heuristic_table_oct = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_octile_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
    heuristic_table_cheby = {
        (r, c): problem.heuristic((r, c), problem.goal, function_h=h_chebyshev_distance)
        for r in range(problem.maze.H) for c in range(problem.maze.W)
    }
        
    # Funções 'f' para os algoritmos
    f_astar: Callable[[Node], float] = lambda n: n.g + n.h
    f_greedy: Callable[[Node], float] = lambda n: n.h

    # --- 4. Loop de Execução Expandido ---
    for _ in range(num_runs):
        
        # --- A* Manhattan ---
        try:
            res, t, _, _, p = measure_time_memory(a_star_table_search, problem, f_astar, heuristic_table_manh)
            if res:
                sol, ne = res
                found['A*-Manhattan'] += 1
                times['A*-Manhattan'].append(t)
                nodes['A*-Manhattan'].append(ne)
                costs['A*-Manhattan'].append(sol.g)
                peaks['A*-Manhattan'].append(p)
        except Exception: pass

        # --- A* Euclidean ---
        try:
            res, t, _, _, p = measure_time_memory(a_star_table_search, problem, f_astar, heuristic_table_euc)
            if res:
                sol, ne = res
                found['A*-Euclidean'] += 1
                times['A*-Euclidean'].append(t)
                nodes['A*-Euclidean'].append(ne)
                costs['A*-Euclidean'].append(sol.g)
                peaks['A*-Euclidean'].append(p)
        except Exception: pass
        
        # --- A* Octile (NOVO) ---
        try:
            res, t, _, _, p = measure_time_memory(a_star_table_search, problem, f_astar, heuristic_table_oct)
            if res:
                sol, ne = res
                found['A*-Octile'] += 1
                times['A*-Octile'].append(t)
                nodes['A*-Octile'].append(ne)
                costs['A*-Octile'].append(sol.g)
                peaks['A*-Octile'].append(p)
        except Exception: pass

        # --- A* Chebyshev (NOVO) ---
        try:
            res, t, _, _, p = measure_time_memory(a_star_table_search, problem, f_astar, heuristic_table_cheby)
            if res:
                sol, ne = res
                found['A*-Chebyshev'] += 1
                times['A*-Chebyshev'].append(t)
                nodes['A*-Chebyshev'].append(ne)
                costs['A*-Chebyshev'].append(sol.g)
                peaks['A*-Chebyshev'].append(p)
        except Exception: pass

        # --- Greedy Manhattan ---
        try:
            res, t, _, _, p = measure_time_memory(greedy_best_first_search, problem, f_greedy, heuristic_table_manh)
            if res:
                sol, ne = res
                found['Greedy-Manhattan'] += 1
                times['Greedy-Manhattan'].append(t)
                nodes['Greedy-Manhattan'].append(ne)
                path = reconstruct_path(sol)
                costs['Greedy-Manhattan'].append(len(path) - 1 if path else 0)
                peaks['Greedy-Manhattan'].append(p)
        except Exception: pass

        # --- Greedy Euclidean ---
        try:
            res, t, _, _, p = measure_time_memory(greedy_best_first_search, problem, f_greedy, heuristic_table_euc)
            if res:
                sol, ne = res
                found['Greedy-Euclidean'] += 1
                times['Greedy-Euclidean'].append(t)
                nodes['Greedy-Euclidean'].append(ne)
                path = reconstruct_path(sol)
                costs['Greedy-Euclidean'].append(len(path) - 1 if path else 0)
                peaks['Greedy-Euclidean'].append(p)
        except Exception: pass

        # --- Greedy Octile (NOVO) ---
        try:
            res, t, _, _, p = measure_time_memory(greedy_best_first_search, problem, f_greedy, heuristic_table_oct)
            if res:
                sol, ne = res
                found['Greedy-Octile'] += 1
                times['Greedy-Octile'].append(t)
                nodes['Greedy-Octile'].append(ne)
                path = reconstruct_path(sol)
                costs['Greedy-Octile'].append(len(path) - 1 if path else 0)
                peaks['Greedy-Octile'].append(p)
        except Exception: pass

        # --- Greedy Chebyshev (NOVO) ---
        try:
            res, t, _, _, p = measure_time_memory(greedy_best_first_search, problem, f_greedy, heuristic_table_cheby)
            if res:
                sol, ne = res
                found['Greedy-Chebyshev'] += 1
                times['Greedy-Chebyshev'].append(t)
                nodes['Greedy-Chebyshev'].append(ne)
                path = reconstruct_path(sol)
                costs['Greedy-Chebyshev'].append(len(path) - 1 if path else 0)
                peaks['Greedy-Chebyshev'].append(p)
        except Exception: pass

    # Calcular estatísticas e formatar
    # (Esta seção não precisa de NENHUMA MUDANÇA,
    # pois ela itera sobre os 'keys_to_test' que já expandimos)
    metrics = {}
    for key in times:
        avg_time = statistics.mean(times[key]) if times[key] else 0
        avg_nodes = statistics.mean(nodes[key]) if nodes[key] else 0
        avg_cost = statistics.mean(costs[key]) if costs[key] else 0
        avg_peak = statistics.mean(peaks[key]) if peaks[key] else 0
        
        metrics[f'{key} avg time (ms)'] = f"{avg_time:.3f}"
        metrics[f'{key} avg nodes'] = f"{avg_nodes:.1f}"
        metrics[f'{key} avg cost'] = f"{avg_cost:.1f}"
        metrics[f'{key} avg peak (KB)'] = f"{(avg_peak / 1024):.3f}"
        metrics[f'{key} found count'] = f"{found[key]}/{num_runs}"
    
    return metrics
