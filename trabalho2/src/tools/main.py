# EXTERNAL IMPORTS
import os, sys, traceback
from pathlib import Path     

# ADJUST SYSTEM PATH TO INCLUDE THE SRC FOLDER FOR MODULE RESOLUTION
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

# INTERNAL PROJECT IMPORTS
# CORE
from core.eight_queens_representation import EightQueensProblem

# GREEDY LOCAL SEARCH
from greedy_local_search.sideways_moves import compute_hill_climbing_with_sideways_moves
from greedy_local_search.random_restarts import compute_hill_climbing_with_random_restarts
from greedy_local_search.simulated_annealing import compute_simulated_annealing

# OPTIONS MENU FUNCTION
def show_options_menu():
    print("Options Menu:")
    print("1. Hill Climbing - Sideways Moves Allowed")
    print("2. Hill Climbing - Random Restarts")
    print("3. Simulated Annealing")
    print("4. Compare Algorithms")
    print("5. Exit")

# ALGORITHM's MENU FUNCTION
def show_algorithm_menu(algorithm: str):
    print(f"Options for {algorithm}:")
    print("1. Run Algorithm")
    print("2. Visualize Search")
    if algorithm == "sideways":
        print("3. Set Sideways Moves Limit (default = 100)")
        print("4. Back to Main Menu")
    elif algorithm == "random_restarts":
        print("3. Allow Sideways Moves")
        print("4. Don't Allow Sideways Moves")
        print("5. Set Max Moves per Restart (default = 100)")
        print("6. Set Max Restarts (default = 100)")
        print("7. Back to Main Menu")
    elif algorithm == "simulated_annealing":
        print("3. Set Initial Temperature (default = 100)")
        print("4. Set Cooling Function (default = linear)")
        print("5. Set Max Steps (default = 1000)")
        print("6. Back to Main Menu")

# GET OPTION FUNCTION
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

# DISPLAY COMPARISON TABLE FOR UNINFORMED SEARCH ALGORITHMS
# def show_comparison_uninformed(metrics):
#     print("\n--- Comparação: Dijkstra vs Bidirectional ---")
#     col_metrica_width = 22  
#     col_data_width = 18     
#     header = (
#         f"{'Métrica':<{col_metrica_width}} | "
#         f"{'Dijkstra':>{col_data_width}} | "
#         f"{'Bidirectional':>{col_data_width}}"
#     )
#     print(header)
#     print(f"{'-' * col_metrica_width} | {'-' * col_data_width} | {'-' * col_data_width}")
#     print(f"{'Tempo médio (ms)':<{col_metrica_width}} | "
#             f"{metrics['Dijkstra avg time (ms)']:>{col_data_width}} | "
#             f"{metrics['Bidirectional avg time (ms)']:>{col_data_width}}")
#     print(f"{'Memória Peak (KB)':<{col_metrica_width}} | "
#             f"{metrics['Dijkstra avg peak (KB)']:>{col_data_width}} | "
#             f"{metrics['Bidirectional avg peak (KB)']:>{col_data_width}}")
#     print(f"{'Memória Current (KB)':<{col_metrica_width}} | "
#             f"{metrics['Dijkstra avg current (KB)']:>{col_data_width}} | "
#             f"{metrics['Bidirectional avg current (KB)']:>{col_data_width}}")
#     print(f"{'Memória RSS (B)':<{col_metrica_width}} | "
#             f"{metrics['Dijkstra avg memory (B)']:>{col_data_width}} | "
#             f"{metrics['Bidirectional avg memory (B)']:>{col_data_width}}")
#     print(f"{'Encontrado':<{col_metrica_width}} | "
#             f"{metrics['Dijkstra found count']:>{col_data_width}} | "
#             f"{metrics['Bidirectional found count']:>{col_data_width}}")
#     print("-" * len(header))
#     print()

# GENERATE GIFS FOR ALGORITHMS
# def show_visualize(problem, matrix):
#     try:
#         current_file = Path(__file__).resolve()
#         repo_root = current_file.parents[2] if 'tools' in str(current_file) else current_file.parents[1]
#     except Exception:
#         repo_root = Path.cwd() 
#     output_dir = repo_root / 'data' / 'output' / 'visualization' / 'uninformed'
#     output_dir.mkdir(parents=True, exist_ok=True) 
#     default_interval = 100
#     algorithm = ['dijkstra', 'bidirectional']
#     for alg in algorithm:
#         out_name = f'visualization-{alg}.gif'
#         out_path = output_dir / out_name
#         try:
#             generate_gifs_uninformed(
#                 problem=problem, 
#                 matrix=matrix, 
#                 algorithm=alg,
#                 interval_ms=default_interval, 
#                 out_file=str(out_path)
#             )
#             print(f"GIF salvo em: {out_path}")
#         except Exception as e:
#             tb = traceback.format_exc()
#             print(f"*** ERRO ao gerar {alg}: {e} ***\n{tb}\n")
#         print("Informed GIF generation complete.")

# MAIN FUNCTION HANDLING MENU INTERACTIONS AND SEARCH EXECUTIONS
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    problem = EightQueensProblem()

    while True:
        show_options_menu()
        option = get_option(5)

        if option == 1:
            sideways_limit = 100
            while True:
                show_algorithm_menu("sideways")
                sub_option = get_option(4)

                if sub_option == 1:
                    print("Running Hill Climbing with Sideways Moves Allowed...")
                    compute_hill_climbing_with_sideways_moves(problem, sideways_limit)
                elif sub_option == 2:
                    print("Visualizing Hill Climbing with Sideways Moves Allowed...")
                    # show_visualize_hill_climbing_sideways(problem)
                elif sub_option == 3:
                    sideways_limit = int(input("Enter the maximum number of sideways moves allowed: "))
                    print(f"Sideways moves limit set to {sideways_limit}.")
                elif sub_option == 4:
                    break
                
            
        elif option == 2:
            allow_sideways = False
            max_moves_per_restart = 100
            max_restarts = 100
            while True:
                show_algorithm_menu("random_restarts")
                sub_option = get_option(7)

                if sub_option == 1:
                    print("Running Hill Climbing with Random Restarts...")
                    compute_hill_climbing_with_random_restarts(problem, allow_sideways, max_moves_per_restart, max_restarts)
                elif sub_option == 2:
                    print("Visualizing Hill Climbing with Random Restarts...")
                    # show_visualize_hill_climbing_with_random_restarts(problem, allow_sideways, max_moves_per_restart)
                elif sub_option == 3:
                    allow_sideways = True
                    print("Sideways moves allowed.")
                elif sub_option == 4:
                    allow_sideways = False
                    print("Sideways moves not allowed.")
                elif sub_option == 5:
                    max_moves_per_restart = int(input("Enter the maximum number of moves per restart: "))
                    print(f"Max moves per restart set to {max_moves_per_restart}.")
                elif sub_option == 6:
                    max_restarts = int(input("Enter the maximum number of restarts: "))
                    print(f"Max restarts set to {max_restarts}.")
                elif sub_option == 7:
                    break

        elif option == 3:
            temperature = 100
            cooling_func = 2 # Default to logarithmic
            max_steps = 1000
            while True:
                show_algorithm_menu("simulated_annealing")
                sub_option = get_option(5)

                if sub_option == 1:
                    compute_simulated_annealing(problem, temperature, cooling_func, True, max_steps)
                elif sub_option == 2:
                    print("Visualizing Simulated Annealing...")
                    # show_visualize_simulated_annealing(problem, temperature, cooling_func)
                elif sub_option == 3:
                    temperature = int(input("Enter the initial temperature: "))
                    print(f"Initial temperature set to {temperature}.")
                elif sub_option == 4:
                    print("Enter the cooling function (linear/logarithmic):")
                    print("1. Linear")
                    print("2. Logarithmic")
                    choice = get_option(2)
                    if choice == 1:
                        cooling_func = 1  # Linear
                    elif choice == 2:
                        cooling_func = 2  # Logarithmic

                    print(f"Cooling function set to {'linear' if cooling_func == 1 else 'logarithmic'}.")
                
                elif sub_option == 5:
                    max_steps = int(input("Enter the maximum number of steps: "))
                    print(f"Max steps set to {max_steps}.")
                elif sub_option == 6:
                    break

        elif option == 4:
            print("Comparing Algorithms...")
            compare_algorithms(problem)

        elif option == 5:
            print("Exiting the program.")
            break

# RUN THE MAIN FUNCTION
if __name__ == "__main__":
    main()