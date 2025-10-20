# EXTERNAL IMPORTS
import os
from pathlib import Path
import traceback                 

# INTERNAL PROJECT IMPORTS
# CORE
from core.maze_problem import MazeProblem
from core.maze_generator import read_matrix_from_file
from core.maze_representation import Maze

# UNINFORMED SEARCH
from uninformed.dijkstra import compute_dijkstra
from uninformed.bidirectional_best_first_search import compute_bidirectional_best_first_search
from uninformed.generate_gifs_uninformed import generate_gifs_uninformed
import uninformed.uninformed_comparison as uc

# INFORMED SEARCH 
from informed.greedy_best_first_search import compute_greedy_best_first_search
from informed.a_star_search import compute_a_star_search
from informed.generate_gifs_informed import generate_gifs_informed  
import informed.informed_comparison as ic

# OPTIONS MENU FUNCTION
def show_options_menu():
    print("Options Menu:")
    print("1. Uninformed Search")
    print("2. Informed Search")
    print("3. Show Generated Graph")
    print("4. Exit")

# UNINFORMED SEARCH MENU FUNCTION
def show_uninformed_menu():
    print("Uninformed Search Options:")
    print("1. Dijkstra")
    print("2. Bidirectional Best-First Search")
    print("3. Comparison of Both")
    print("4. Visualize Uninformed Searches")
    print("5. Back to Main Menu")

# INFORMED SEARCH MENU FUNCTION
def show_informed_menu():
    print("Informed Search Options:")
    print("1. A* Search")
    print("2. Greedy Best-First Search")
    print("3. Comparison of A* and Greedy Best-First Search")
    print("4. Visualize Informed Searches")
    print("5. Back to Main Menu")

# HEURISTIC MENU FUNCTION
def show_heuristic_menu(algorithm: str):
    print(f"Heuristic Options for {algorithm}:")
    print("1. Manhattan Distance")
    print("2. Euclidean Distance")
    print("3. Octile Distance")
    print("4. Chebyshev Distance")
    print("5. Back to Previous Menu")

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
def show_comparison_uninformed(metrics):
    print("\n--- Comparação: Dijkstra vs Bidirectional ---")
    col_metrica_width = 22  
    col_data_width = 18     
    header = (
        f"{'Métrica':<{col_metrica_width}} | "
        f"{'Dijkstra':>{col_data_width}} | "
        f"{'Bidirectional':>{col_data_width}}"
    )
    print(header)
    print(f"{'-' * col_metrica_width} | {'-' * col_data_width} | {'-' * col_data_width}")
    print(f"{'Tempo médio (ms)':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg time (ms)']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg time (ms)']:>{col_data_width}}")
    print(f"{'Nós médios':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg nodes']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg nodes']:>{col_data_width}}")
    print(f"{'Custo médio':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg cost']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg cost']:>{col_data_width}}")
    print(f"{'Memória Peak (KB)':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg peak (KB)']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg peak (KB)']:>{col_data_width}}")
    print(f"{'Memória Current (KB)':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg current (KB)']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg current (KB)']:>{col_data_width}}")
    print(f"{'Memória RSS (B)':<{col_metrica_width}} | "
            f"{metrics['Dijkstra avg memory (B)']:>{col_data_width}} | "
            f"{metrics['Bidirectional avg memory (B)']:>{col_data_width}}")
    print(f"{'Encontrado':<{col_metrica_width}} | "
            f"{metrics['Dijkstra found count']:>{col_data_width}} | "
            f"{metrics['Bidirectional found count']:>{col_data_width}}")
    print("-" * len(header))
    print()

# GENERATE GIFS FOR UNINFORMED SEARCH ALGORITHMS
def show_visualize_uninformed(problem, matrix):
    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file.parents[2] if 'tools' in str(current_file) else current_file.parents[1]
    except Exception:
        repo_root = Path.cwd() 
    output_dir = repo_root / 'data' / 'output' / 'visualization' / 'uninformed'
    output_dir.mkdir(parents=True, exist_ok=True) 
    default_interval = 100
    algorithm = ['dijkstra', 'bidirectional']
    for alg in algorithm:
        out_name = f'visualization-{alg}.gif'
        out_path = output_dir / out_name
        try:
            generate_gifs_uninformed(
                problem=problem, 
                matrix=matrix, 
                algorithm=alg,
                interval_ms=default_interval, 
                out_file=str(out_path)
            )
            print(f"GIF salvo em: {out_path}")
        except Exception as e:
            tb = traceback.format_exc()
            print(f"*** ERRO ao gerar {alg}: {e} ***\n{tb}\n")
        print("Informed GIF generation complete.")

# DISPLAY COMPARISON TABLE FOR INFORMED SEARCH ALGORITHMS
def show_comparison_informed(metrics):
    print("\n--- Comparação: Algoritmos Informados (A* vs Greedy) ---")                    
    col_metrica_width = 20 
    col_data_width = 12 
    headers = (
        "Métrica",
        "A*-Manhattan", "A*-Euclidean", "A*-Octile", "A*-Chebyshev",
        "G-Manhattan", "G-Euclidean", "G-Octile", "G-Chebyshev"
    )
    header_line = (
        f"{headers[0]:<{col_metrica_width}} | "
        f"{headers[1]:>{col_data_width}} | {headers[2]:>{col_data_width}} | {headers[3]:>{col_data_width}} | {headers[4]:>{col_data_width}} | "
        f"{headers[5]:>{col_data_width}} | {headers[6]:>{col_data_width}} | {headers[7]:>{col_data_width}} | {headers[8]:>{col_data_width}}"
    )
    print(header_line)
    separator = (
        f"{'-' * col_metrica_width} | "
        f"{'-' * col_data_width} | {'-' * col_data_width} | {'-' * col_data_width} | {'-' * col_data_width} | "
        f"{'-' * col_data_width} | {'-' * col_data_width} | {'-' * col_data_width} | {'-' * col_data_width}"
    )
    print(separator)
    print(f"{'Tempo médio (ms)':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg time (ms)']:>{col_data_width}} | {metrics['A*-Euclidean avg time (ms)']:>{col_data_width}} | {metrics['A*-Octile avg time (ms)']:>{col_data_width}} | {metrics['A*-Chebyshev avg time (ms)']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg time (ms)']:>{col_data_width}} | {metrics['Greedy-Euclidean avg time (ms)']:>{col_data_width}} | {metrics['Greedy-Octile avg time (ms)']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg time (ms)']:>{col_data_width}}")
    print(f"{'Nós médios':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg nodes']:>{col_data_width}} | {metrics['A*-Euclidean avg nodes']:>{col_data_width}} | {metrics['A*-Octile avg nodes']:>{col_data_width}} | {metrics['A*-Chebyshev avg nodes']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg nodes']:>{col_data_width}} | {metrics['Greedy-Euclidean avg nodes']:>{col_data_width}} | {metrics['Greedy-Octile avg nodes']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg nodes']:>{col_data_width}}")
    print(f"{'Custo médio':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg cost']:>{col_data_width}} | {metrics['A*-Euclidean avg cost']:>{col_data_width}} | {metrics['A*-Octile avg cost']:>{col_data_width}} | {metrics['A*-Chebyshev avg cost']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg cost']:>{col_data_width}} | {metrics['Greedy-Euclidean avg cost']:>{col_data_width}} | {metrics['Greedy-Octile avg cost']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg cost']:>{col_data_width}}")
    print(f"{'Memória Peak (KB)':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg peak (KB)']:>{col_data_width}} | {metrics['A*-Euclidean avg peak (KB)']:>{col_data_width}} | {metrics['A*-Octile avg peak (KB)']:>{col_data_width}} | {metrics['A*-Chebyshev avg peak (KB)']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg peak (KB)']:>{col_data_width}} | {metrics['Greedy-Euclidean avg peak (KB)']:>{col_data_width}} | {metrics['Greedy-Octile avg peak (KB)']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg peak (KB)']:>{col_data_width}}")
    print(f"{'Memória Current (KB)':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg current (KB)']:>{col_data_width}} | {metrics['A*-Euclidean avg current (KB)']:>{col_data_width}} | {metrics['A*-Octile avg current (KB)']:>{col_data_width}} | {metrics['A*-Chebyshev avg current (KB)']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg current (KB)']:>{col_data_width}} | {metrics['Greedy-Euclidean avg current (KB)']:>{col_data_width}} | {metrics['Greedy-Octile avg current (KB)']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg current (KB)']:>{col_data_width}}")
    print(f"{'Memória RSS (B)':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan avg memory (B)']:>{col_data_width}} | {metrics['A*-Euclidean avg memory (B)']:>{col_data_width}} | {metrics['A*-Octile avg memory (B)']:>{col_data_width}} | {metrics['A*-Chebyshev avg memory (B)']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan avg memory (B)']:>{col_data_width}} | {metrics['Greedy-Euclidean avg memory (B)']:>{col_data_width}} | {metrics['Greedy-Octile avg memory (B)']:>{col_data_width}} | {metrics['Greedy-Chebyshev avg memory (B)']:>{col_data_width}}")
    print(f"{'Encontrado':<{col_metrica_width}} | "
            f"{metrics['A*-Manhattan found count']:>{col_data_width}} | {metrics['A*-Euclidean found count']:>{col_data_width}} | {metrics['A*-Octile found count']:>{col_data_width}} | {metrics['A*-Chebyshev found count']:>{col_data_width}} | "
            f"{metrics['Greedy-Manhattan found count']:>{col_data_width}} | {metrics['Greedy-Euclidean found count']:>{col_data_width}} | {metrics['Greedy-Octile found count']:>{col_data_width}} | {metrics['Greedy-Chebyshev found count']:>{col_data_width}}")
    print(separator)
    print()

# GENERATE GIFS FOR INFORMED SEARCH ALGORITHMS WITH MULTIPLE HEURISTICS
def show_visualize_informed(problem, matrix):
    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file.parents[2] if 'tools' in str(current_file) else current_file.parents[1]
    except Exception:
        repo_root = Path.cwd() 
    output_dir = repo_root / 'data' / 'output' / 'visualization' / 'informed'
    output_dir.mkdir(parents=True, exist_ok=True) 
    default_interval = 100
    combos = [
        ('a_star', 'manhattan'),
        ('a_star', 'euclidean'),
        ('a_star', 'octile'),
        ('a_star', 'chebyshev'),
        ('greedy', 'manhattan'),
        ('greedy', 'euclidean'),
        ('greedy', 'octile'),
        ('greedy', 'chebyshev'),
    ]
    print(f"Generating {len(combos)} GIFs in {output_dir}...")
    for alg, heur in combos:
        out_name = f'visualization-{alg}-{heur}.gif'
        out_path = output_dir / out_name
        try:
            generate_gifs_informed(
                problem=problem, 
                matrix=matrix, 
                heuristic=heur, 
                algorithm=alg,
                interval_ms=default_interval, 
                out_file=str(out_path)  
            )
            print(f"GIF salvo em: {out_path}")
        except Exception as e:
            tb = traceback.format_exc()
            print(f"*** ERRO ao gerar {alg}-{heur}: {e} ***\n{tb}\n")
    print("Informed GIF generation complete.")

# MAIN FUNCTION HANDLING MENU INTERACTIONS AND SEARCH EXECUTIONS
def main():  
    script_dir = os.path.dirname(os.path.abspath(__file__))
    maze_path = os.path.join(script_dir, "..", "..", "data", "input", "maze.txt")

    matrix = read_matrix_from_file(os.path.join(script_dir, '..', "..", 'data', 'input', 'maze.txt'))

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
                    metrics = uc.compare_uninformed_search_algorithms(matrix)
                    show_comparison_uninformed(metrics)
                    
                elif sub_option == 4:
                    print("Visualizing Uninformed Searches (Dijkstra and Bidirectional)...")
                    show_visualize_uninformed(problem, matrix)

                elif sub_option == 5:
                    break
            
        elif option == 2:
            while True:
                show_informed_menu()
                sub_option = get_option(5)
                if sub_option == 1:
                    while True:
                        show_heuristic_menu("A* Search")
                        heuristic_option = get_option(5)
                        if heuristic_option == 1:
                            print("A* Search with Manhattan Distance selected.")
                            compute_a_star_search(problem, heuristic="manhattan")
                            break
                        elif heuristic_option == 2:
                            print("A* Search with Euclidean Distance selected.")
                            compute_a_star_search(problem, heuristic="euclidean")
                            break
                        elif heuristic_option == 3:
                            print("A* Search with Octile Distance selected.")
                            compute_a_star_search(problem, heuristic="octile")
                            break
                        elif heuristic_option == 4:
                            print("A* Search with Chebyshev Distance selected.")
                            compute_a_star_search(problem, heuristic="chebyshev")
                            break
                        elif heuristic_option == 5:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 2:
                    while True:
                        show_heuristic_menu("Greedy Best-First Search")
                        heuristic_option = get_option(5)
                        if heuristic_option == 1:
                            print("Greedy Best-First Search with Manhattan Distance selected.")
                            compute_greedy_best_first_search(problem, heuristic="manhattan")
                            break
                        elif heuristic_option == 2:
                            print("Greedy Best-First Search with Euclidean Distance selected.")
                            compute_greedy_best_first_search(problem, heuristic="euclidean")
                            break
                        elif heuristic_option == 3:
                            print("Greedy Best-First Search with Octile Distance selected.")
                            compute_greedy_best_first_search(problem, heuristic="octile")
                            break
                        elif heuristic_option == 4:
                            print("Greedy Best-First Search with Chebyshev Distance selected.")
                            compute_greedy_best_first_search(problem, heuristic="chebyshev")
                            break
                        elif heuristic_option == 5:
                            break
                        else:
                            print("Invalid option. Please try again.")
                            continue

                elif sub_option == 3:
                    print("Comparison of A* and Greedy Best-First Search selected.")
                    metrics = ic.compare_informed_search_algorithms(matrix, 15)
                    show_comparison_informed(metrics)

                elif sub_option == 4: 
                    print("Visualizing Informed Searches (A*/Greedy x 4 Heuristics)...")
                    show_visualize_informed(problem, matrix)
                
                elif sub_option == 5:
                    break

        elif option == 3:
            print("Generated Graph:")
            for node, edges in mz.to_graph().items():
                print(f"{node}: {edges}")

        elif option == 4:
            print("Exiting the program.")
            break
        
# RUN THE MAIN FUNCTION
if __name__ == "__main__":
    main()
