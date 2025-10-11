# Options Menu

def show_options_menu():
    print("Options Menu:")
    print("1. Uninformed Search")
    print("2. Informed Search")
    print("3. Show Generated Graph")
    print("4. Exit")

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
    import os

    # Compute the path to the maze file relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maze_path = os.path.join(script_dir, "..", "data", "input", "maze.txt")

    from maze_problem import MazeProblem
    from uninformed_search.djikstra import djikstra
    from best_first_search import reconstruct_path

    matrix = read_matrix_from_file("data/input/maze.txt")
    graph = generate_graph_from_matrix(matrix)
    problem = MazeProblem(matrix, graph)
    
    while True:
        show_options_menu()
        option = get_option()

        if option == 1:
            print("Uninformed Search selected.")
            goal_node = djikstra(problem)
            if goal_node:
                path = reconstruct_path(goal_node)
                print("Path:", path)
            else:
                print("No path found")
        elif option == 2:
            print("Informed Search selected.")
            # Call informed search function here
        elif option == 3:
            print("Generated Graph:")
            for node, edges in graph.items():
                print(f"{node}: {edges}")
        elif option == 4:
            print("Exiting the program.")
            break
        
# Run the main function
if __name__ == "__main__":
    main()