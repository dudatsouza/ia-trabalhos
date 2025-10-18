# Options Menu

def show_options_menu():
    print("Options Menu:")
    print("1. Uninformed Search")
    print("2. Informed Search")
    print("3. Show Generated Graph")
    print("4. Exit")

def show_uninformed_menu():
    print("Uninformed Search Options:")
    print("1. Dijkstra")
    print("2. Bidirectional Best-First Search")
    print("3. Comparison of Both")
    print("4. Visualize Uninformed Searches")
    print("5. Back to Main Menu")

def show_informed_menu():
    print("Informed Search Options:")
    print("1. A* Search")
    print("2. Greedy Best-First Search")
    print("3. Comparison of A* and Greedy Best-First Search")
    print("4. Comparison of Heuristics")
    print("5. Back to Main Menu")

def show_heuristic_menu(algorithm: str):
    print(f"Heuristic Options for {algorithm}:")
    print("1. Manhattan Distance")
    print("2. Euclidean Distance")
    print("3. Back to Previous Menu")


def _collect_tree_nodes(snapshots):
    nodes = set()
    for snap in snapshots:
        if snap.get('reached'):
            nodes.update(tuple(state) for state in snap['reached'])
        for key in ('reached_F', 'reached_B'):
            if key in snap:
                nodes.update(tuple(state) for state in snap[key])
    return nodes

def get_option(max_option: int = 5) -> int:
    while True:
        try:
            option = int(input(f"Choose an option (1-{max_option}): "))
            if 1 <= option <= max_option:
                return option
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Main Function
def main():
    # Import maze utilities (module name uses underscore)
    from maze_generator import read_matrix_from_file, generate_graph_from_matrix
    from maze_representation import Maze
    from measure_time_memory import measure_time_memory
    import os
    

    # Compute the path to the maze file relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maze_path = os.path.join(script_dir, "..", "data", "input", "maze.txt")

    from maze_problem import MazeProblem
    from uninformed_search.dijkstra import dijkstra
    from uninformed_search.bidirectional_best_first_search import bidirectional_best_first_search
    from best_first_search import reconstruct_path

    matrix = read_matrix_from_file(os.path.join(script_dir, '..', 'data', 'input', 'maze.txt'))
    # Use Maze representation as primary
    mz = Maze(matrix)
    problem = MazeProblem(mz)
    s = mz.start
    print("Valid actions from start:", mz.actions(s))
    
    while True:
        show_options_menu()
        option = get_option(4)

        if option == 1:
            while True:
                show_uninformed_menu()
                sub_option = get_option(5)
                if sub_option == 1:
                    print("Dijkstra selected.")
                    # If not found, returns None

                    result, elapsed_time, memory_used, current, peak = measure_time_memory(dijkstra, problem)

                    if result is None:
                        print("No path found")
                        continue
                    
                    goal_node, nodes_expanded = result

                    if goal_node:
                        path = reconstruct_path(goal_node)
                        print("Path:", path)
                        print("Number of nodes expanded:", nodes_expanded)
                        print("Cost of path:", goal_node.g)
                        print(f"Time taken: {elapsed_time:.3f} milliseconds")
                        print(f"Memory used: {memory_used:.12f} B")
                        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

                elif sub_option == 2:
                    print("Bidirectional Best-First Search selected.")
                    # Problem 1 is Forward and Problem 2 is Backward
                    # Change char "S" to "G" and "G" to "S" in matrix
                    
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

                    result, elapsed_time, memory_used, current, peak = measure_time_memory(bid_bfs)
                    
                    if result is None:
                        print("No path found")
                        continue

                    solution, nodes_expanded = result

                    if solution:
                        path = reconstruct_path(solution)
                        print("Path:", path)
                        print("Number of nodes expanded:", nodes_expanded)
                        print("Cost of path:", solution.g)
                        print(f"Time taken: {elapsed_time:.3f} milliseconds")
                        print(f"Memory used: {memory_used:.12f} B")
                        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

                elif sub_option == 3:
                    print("Comparison of Dijkstra and Bidirectional Best-First Search selected.")
                    # Run both algorithms 15 times and average the time and memory usage
                    # Compare nodes expanded as well as the found path
                    import statistics
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

                elif sub_option == 4:
                    # Visualize Bidirectional Best-First Search
                    print("Visualizing Bidirectional Best-First Search...")
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
                    import visualize_matrix

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
                            out_path = os.path.join(script_dir, '..', 'visualization-bid-bfs.gif')
                            print(f'Saving visualization to {out_path}')
                            visualize_matrix.visualize(
                                os.path.join(script_dir, '..', 'data', 'input', 'maze.txt'),
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
                            out_path = os.path.join(script_dir, '..', 'visualization-dijkstra.gif')
                            print(f'Saving visualization to {out_path}')
                            visualize_matrix.visualize(
                                os.path.join(script_dir, '..', 'data', 'input', 'maze.txt'),
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

                elif sub_option == 5:
                    break
            
        elif option == 2:
            while True:
                show_informed_menu()
                sub_option = get_option(5)
                if sub_option == 1:
                    while True:
                        show_heuristic_menu("A* Search")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            print("A* Search with Manhattan Distance selected.")
                            break
                        elif heuristic_option == 2:
                            print("A* Search with Euclidean Distance selected.")
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 2:
                    while True:
                        show_heuristic_menu("Greedy Best-First Search")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            print("Greedy Best-First Search with Manhattan Distance selected.")
                            break
                        elif heuristic_option == 2:
                            print("Greedy Best-First Search with Euclidean Distance selected.")
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 3:
                    print("Comparison of A* and Greedy Best-First Search selected.")
                elif sub_option == 4:
                    print("Comparison of Heuristics selected.")
                elif sub_option == 5:
                    break

        elif option == 3:
            print("Generated Graph:")
            for node, edges in mz.to_graph().items():
                print(f"{node}: {edges}")
        elif option == 4:
            print("Exiting the program.")
            break
        
# Run the main function
if __name__ == "__main__":
    main()