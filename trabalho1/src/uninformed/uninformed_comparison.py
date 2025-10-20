# EXTERNAL IMPORTS
import statistics
from pathlib import Path
import json

# INTERNAL PROJECT IMPORTS
# UNINFORMED SEARCH
from uninformed.bidirectional_best_first_search import bidirectional_best_first_search
from uninformed.dijkstra import dijkstra

# CORE
from core.maze_problem import MazeProblem
from core.maze_representation import Maze

# SEARCH
from search.best_first_search import best_first_search
from search.measure_time_memory import measure_time_memory

# COMPARISON 
from comparisons.uninformed_plots import plot_uninformed_metrics


# COMPARE DIJKSTRA AND BIDIRECTIONAL BEST-FIRST SEARCH
def compare_uninformed_search_algorithms(matrix):
    # PREPARE MAZE AND PROBLEM
    mz = Maze(matrix)
    problem = MazeProblem(mz)
    
    # --- DATA COLLECTION FOR METRICS ---
    dijkstra_times = []
    dijkstra_memories = []
    dijkstra_nodes_expanded = []
    dijkstra_currents = []
    dijkstra_peaks = []
    dijkstra_costs = []
    dijkstra_total_path_found = 0

    bid_bfs_times = []
    bid_bfs_memories = []
    bid_bfs_nodes_expanded = []
    bid_bfs_currents = []
    bid_bfs_peaks = []
    bid_bfs_costs = []
    bid_bfs_total_path_found = 0

    # AUXILIARY FUNCTION FOR BIDIRECTIONAL BEST-FIRST SEARCH
    def bid_bfs():
        # PREPARE A REVERSED MATRIX FOR BIDIRECTIONAL SEARCH
        matrix_2 = [row[:] for row in matrix]  
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S':
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G':
                    matrix_2[r][c] = 'S'
        mz_2 = Maze(matrix_2)
        problem_2 = MazeProblem(mz_2)
        # RUN BIDIRECTIONAL BEST-FIRST SEARCH
        return bidirectional_best_first_search(
            problem_F=problem,
            f_F=lambda n: n.g,
            problem_B=problem_2,
            f_B=lambda n: n.g
        )

    # LOOP TO COLLECT METRICS (15 TIMES)
    for _ in range(15):
        # --- DIJKSTRA ---
        result_dij, elapsed_time_dij, memory_used_dij, current_dij, peak_dij = measure_time_memory(dijkstra, problem)
        if result_dij is not None:
            solution, nodes_expanded_dij = result_dij
            dijkstra_total_path_found += 1
            dijkstra_times.append(elapsed_time_dij)
            dijkstra_memories.append(memory_used_dij)
            dijkstra_nodes_expanded.append(nodes_expanded_dij)
            dijkstra_currents.append(current_dij)
            dijkstra_peaks.append(peak_dij)
            dijkstra_costs.append(solution.g)

        # --- BIDIRECTIONAL BEST-FIRST SEARCH ---
        result_bfs, elapsed_time_bfs, memory_used_bfs, current_bfs, peak_bfs = measure_time_memory(bid_bfs)
        if result_bfs is not None:
            solution, nodes_expanded_bfs = result_bfs
            bid_bfs_total_path_found += 1
            bid_bfs_times.append(elapsed_time_bfs)
            bid_bfs_memories.append(memory_used_bfs)
            bid_bfs_nodes_expanded.append(nodes_expanded_bfs)
            bid_bfs_currents.append(current_bfs)
            bid_bfs_peaks.append(peak_bfs)
            bid_bfs_costs.append(solution.g)

    # --- CALCULATE AVERAGES ---
    avg_dijkstra_time = statistics.mean(dijkstra_times) if dijkstra_times else 0
    avg_dijkstra_memory = statistics.mean(dijkstra_memories) if dijkstra_memories else 0
    avg_dijkstra_nodes_expanded = statistics.mean(dijkstra_nodes_expanded) if dijkstra_nodes_expanded else 0
    avg_dijkstra_currents = statistics.mean(dijkstra_currents) if dijkstra_currents else 0
    avg_dijkstra_peaks = statistics.mean(dijkstra_peaks) if dijkstra_peaks else 0
    avg_dijkstra_costs = statistics.mean(dijkstra_costs) if dijkstra_costs else 0

    avg_bid_bfs_time = statistics.mean(bid_bfs_times) if bid_bfs_times else 0
    avg_bid_bfs_memory = statistics.mean(bid_bfs_memories) if bid_bfs_memories else 0
    avg_bid_bfs_nodes_expanded = statistics.mean(bid_bfs_nodes_expanded) if bid_bfs_nodes_expanded else 0
    avg_bid_bfs_currents = statistics.mean(bid_bfs_currents) if bid_bfs_currents else 0
    avg_bid_bfs_peaks = statistics.mean(bid_bfs_peaks) if bid_bfs_peaks else 0
    avg_bid_bfs_costs = statistics.mean(bid_bfs_costs) if bid_bfs_costs else 0

    # RETURN DICTIONARY WITH ALL METRICS
    metrics = {
        'Dijkstra avg time (ms)': f"{avg_dijkstra_time:.3f}",
        'Dijkstra avg memory (B)': f"{avg_dijkstra_memory:.3f}",
        'Dijkstra avg nodes': f"{avg_dijkstra_nodes_expanded:.1f}",
        'Dijkstra avg current (KB)': f"{(avg_dijkstra_currents / 1024):.3f}",
        'Dijkstra avg peak (KB)': f"{(avg_dijkstra_peaks / 1024):.3f}",
        'Dijkstra found count': f"{dijkstra_total_path_found}/15",
        'Dijkstra avg cost': f"{avg_dijkstra_costs:.3f}",

        'Bidirectional avg time (ms)': f"{avg_bid_bfs_time:.3f}",
        'Bidirectional avg memory (B)': f"{avg_bid_bfs_memory:.3f}",
        'Bidirectional avg nodes': f"{avg_bid_bfs_nodes_expanded:.1f}",
        'Bidirectional avg current (KB)': f"{(avg_bid_bfs_currents / 1024):.3f}",
        'Bidirectional avg peak (KB)': f"{(avg_bid_bfs_peaks / 1024):.3f}", 
        'Bidirectional found count': f"{bid_bfs_total_path_found}/15",
        'Bidirectional avg cost': f"{avg_bid_bfs_costs:.3f}",
    }

    output_filename = '././data/output/metrics/metrics_uninformed.json'

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)

    print(f"Métricas salvas em {output_filename}")

    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    example_path = repo_root / 'data' / 'output' / 'metrics' / 'metrics_uninformed.json'    
    if example_path.exists():
        plot_uninformed_metrics(metrics)
    else:
        print("EXAMPLE METRICS JSON NOT FOUND:", example_path)

    return metrics
