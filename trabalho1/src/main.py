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
    print("4. Back to Main Menu")

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

def get_option():
    while True:
        try:
            option = int(input("Choose an option (1-4): "))
            if option in [1, 2, 3, 4]:
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
    import os

    # Compute the path to the maze file relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maze_path = os.path.join(script_dir, "..", "data", "input", "maze.txt")

    from maze_problem import MazeProblem
    from uninformed_search.djikstra import djikstra
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
        option = get_option()

        if option == 1:
            while True:
                show_uninformed_menu()
                sub_option = get_option()
                if sub_option == 1:
                    print("Dijkstra selected.")
                    # If not found, returns None
                    result = djikstra(problem)
                    if result is None:
                        print("No path found")
                        continue
                    
                    goal_node, nodes_expanded = result

                    if goal_node:
                        path = reconstruct_path(goal_node)
                        print("Path:", path)
                        print("Number of nodes expanded:", nodes_expanded)

                elif sub_option == 2:
                    print("Bidirectional Best-First Search selected.")
                    # Problem 1 is Forward and Problem 2 is Backward
                    # Change char "S" to "G" and "G" to "S" in matrix
                    matrix_2 = [row[:] for row in matrix]  # Deep copy of the matrix
                    for r in range(len(matrix_2)):
                        for c in range(len(matrix_2[0])):
                            if matrix_2[r][c] == 'S':
                                matrix_2[r][c] = 'G'
                            elif matrix_2[r][c] == 'G':
                                matrix_2[r][c] = 'S'
                    mz_2 = Maze(matrix_2)
                    problem_2 = MazeProblem(mz_2)
                    result = bidirectional_best_first_search(problem_F=problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g)
                    if result is None:
                        print("No path found")
                        continue

                    solution, nodes_expanded = result

                    if solution:
                        path = reconstruct_path(solution)
                        print("Path:", path)
                        print("Number of nodes expanded:", nodes_expanded)

                elif sub_option == 3:
                    print("Comparison of Dijkstra and Bidirectional Best-First Search selected.")


                elif sub_option == 4:
                    break
            
        elif option == 2:
            while True:
                show_informed_menu()
                sub_option = get_option()
                if sub_option == 1:
                    while True:
                        show_heuristic_menu("A* Search")
                        heuristic_option = get_option()
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
                        heuristic_option = get_option()
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