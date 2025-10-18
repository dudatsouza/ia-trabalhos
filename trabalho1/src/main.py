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
    print("5. Visualize Informed Searches")
    print("6. Back to Main Menu")

def show_heuristic_menu(algorithm: str):
    print(f"Heuristic Options for {algorithm}:")
    print("1. Manhattan Distance")
    print("2. Euclidean Distance")
    print("3. Back to Previous Menu")

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
    from uninformed_search.dijkstra import compute_dijkstra, dijkstra
    from uninformed_search.bidirectional_best_first_search import bidirectional_best_first_search, compute_bidirectional_best_first_search
    from best_first_search import reconstruct_path

    # from informed_search.a_star_search import compute_a_star_search
    from informed_search.greedy_best_first_search import compute_greedy_best_first_search

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
                    compute_dijkstra(problem)

                elif sub_option == 2:
                    print("Bidirectional Best-First Search selected.")
                    compute_bidirectional_best_first_search(problem, matrix)

                elif sub_option == 3:
                    print("Comparison of Dijkstra and Bidirectional Best-First Search selected.")
                    import uninformed_search.uninformed_comparison as uc
                    uc.compare_uninformed_search_algorithms(matrix)

                elif sub_option == 4:
                    # Visualize Bidirectional Best-First Search
                    print("Visualizing Bidirectional Best-First Search...")
                    from uninformed_search.generate_gifs_uninformed import generate_gifs_uninformed
                    generate_gifs_uninformed(problem, matrix)

                elif sub_option == 5:
                    break
            
        elif option == 2:
            while True:
                show_informed_menu()
                sub_option = get_option(6)
                if sub_option == 1:
                    while True:
                        show_heuristic_menu("A* Search")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            print("A* Search with Manhattan Distance selected.")
                            # Call the A* search function with the selected heuristic
                            compute_a_star_search(problem, heuristic="manhattan")
                            break
                        elif heuristic_option == 2:
                            print("A* Search with Euclidean Distance selected.")
                            compute_a_star_search(problem, heuristic="euclidean")
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
                            compute_greedy_best_first_search(problem, heuristic="manhattan")
                            break
                        elif heuristic_option == 2:
                            print("Greedy Best-First Search with Euclidean Distance selected.")
                            compute_greedy_best_first_search(problem, heuristic="euclidean")
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 3:
                    print("Comparison of A* and Greedy Best-First Search selected.")
                    # Choose heuristics for A* 
                    heuristic_a_star = ""
                    heuristic_greedy = ""
                    while True:
                        show_heuristic_menu("A* Search for Comparison")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            heuristic_a_star = "manhattan"
                            break
                        elif heuristic_option == 2:
                            heuristic_a_star = "euclidean"
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue
                    while True:
                        show_heuristic_menu("Greedy Best-First Search for Comparison")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            heuristic_greedy = "manhattan"
                            break
                        elif heuristic_option == 2:
                            heuristic_greedy = "euclidean"
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue
                    import informed_search.informed_comparison as ic
                    ic.compare_informed_search_algorithms(problem, heuristic_a_star, heuristic_greedy)

                elif sub_option == 4:
                    print("Comparison of Heuristics selected.")
                elif sub_option == 5:
                    print("Visualization of Informed Searches selected.")
                    # Call the function to generate GIFs for informed searches
                    from informed_search.generate_gifs_informed import generate_gifs_informed
                    while True:
                        show_heuristic_menu("Greedy Best-First Search")
                        heuristic_option = get_option(3)
                        if heuristic_option == 1:
                            generate_gifs_informed(problem, matrix, heuristic="manhattan")
                            break
                        elif heuristic_option == 2:
                            generate_gifs_informed(problem, matrix, heuristic="euclidean")
                            break
                        elif heuristic_option == 3:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 6:
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