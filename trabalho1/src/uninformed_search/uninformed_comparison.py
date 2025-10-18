import statistics

from uninformed_search.bidirectional_best_first_search import bidirectional_best_first_search
from best_first_search import best_first_search
from uninformed_search.dijkstra import dijkstra
from maze_problem import MazeProblem
from maze_representation import Maze
from measure_time_memory import measure_time_memory

def compare_uninformed_search_algorithms(matrix):
    mz = Maze(matrix)
    problem = MazeProblem(mz)
    
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

    def bid_bfs():
        matrix_2 = [row[:] for row in matrix]  
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S':
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G':
                    matrix_2[r][c] = 'S'
        mz_2 = Maze(matrix_2)
        problem_2 = MazeProblem(mz_2)
        return bidirectional_best_first_search(problem_F=problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g)

    for _ in range(15):
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

    # Compute average times and memory usage
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

    print(f"Average Dijkstra time: {avg_dijkstra_time:.3f} ms")
    print(f"Average Dijkstra memory: {avg_dijkstra_memory:.3f} B")
    print(f"Average Dijkstra nodes expanded: {avg_dijkstra_nodes_expanded}")
    print(f"Average Dijkstra current memory: {(avg_dijkstra_currents / 1024):.3f} KB")
    print(f"Average Dijkstra peak memory: {(avg_dijkstra_peaks / 1024):.3f} KB")
    print(f"Paths found by Dijkstra: {dijkstra_total_path_found} out of 15")
    print(f"Average Dijkstra cost: {avg_dijkstra_costs:.3f}")

    print(f"Average Bidirectional BFS time: {avg_bid_bfs_time:.3f} ms")
    print(f"Average Bidirectional BFS memory: {avg_bid_bfs_memory:.3f} B")
    print(f"Average Bidirectional BFS nodes expanded: {avg_bid_bfs_nodes_expanded}")
    print(f"Average Bidirectional BFS current memory: {(avg_bid_bfs_currents / 1024):.3f} KB")
    print(f"Average Bidirectional BFS peak memory: {(avg_bid_bfs_peaks):.3f} KB")
    print(f"Paths found by Bidirectional BFS: {bid_bfs_total_path_found} out of 15")
    print(f"Average Bidirectional BFS cost: {avg_bid_bfs_costs:.3f}")