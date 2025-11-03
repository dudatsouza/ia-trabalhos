# EXTERNAL IMPORTS
import random
import os, sys, traceback
from pathlib import Path     

# ADJUST SYSTEM PATH TO INCLUDE THE SRC FOLDER FOR MODULE RESOLUTION
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

# INTERNAL PROJECT IMPORTS
# CORE
from core.eight_queens_representation import EightQueensProblem

# GREEDY LOCAL SEARCH
from local_search.sideways_moves import compute_hill_climbing_with_sideways_moves, hill_climbing_with_sideways_moves
from local_search.random_restarts import compute_hill_climbing_with_random_restarts, hill_climbing_with_random_restarts
from local_search.simulated_annealing import compute_simulated_annealing, simulated_annealing

# COMPARISON
from comparisons.compare_hill_climbing import compare_hill_climbing_algorithms

# VISUALIZATION
from visualization.queen_gif import generate_gif_from_states

# OPTIONS MENU FUNCTION
def show_options_menu():
    print("\n" + "="*50)
    print("  EIGHT QUEENS - HILL CLIMBING ALGORITHMS")
    print("="*50)
    print("1. Hill Climbing - Sideways Moves Allowed")
    print("2. Hill Climbing - Random Restarts")
    print("3. Simulated Annealing")
    print("4. Compare Algorithms")
    print("5. Generate New Random Board")
    print("6. Exit")
    print("="*50)

# ALGORITHM's MENU FUNCTION
def show_algorithm_menu(algorithm: str):
    print(f"\n--- Options for {algorithm.replace('_', ' ').title()} ---")
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
        print("3. Set Initial Temperature (default = 400)")
        print("4. Set Cooling Function (default = exponential)")
        print("5. Set Max Steps (default = 1000)")
        print("6. Back to Main Menu")
    print("-" * 40)

# GET OPTION FUNCTION
def get_option(max_option: int = 6) -> int:
    while True:
        try:
            option = int(input(f"Choose an option (1-{max_option}): "))
            if 1 <= option <= max_option:
                return option
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# BOARD MANAGEMENT FUNCTION
def show_current_board(problem):
    """Display the current board state."""
    board = problem.initial_board()
    conflicts = problem.conflicts(board)
    print(f"\nCurrent board conflicts: {conflicts}")
    print("Board state (column positions for each row):", list(board))
    
    # Visual representation
    print("\nBoard visualization:")
    for row in range(8):
        line = ""
        for col in range(8):
            if board[col] == row:
                line += "Q "
            else:
                line += ". "
        print(line)
    print()

# VISUALIZATION FUNCTION
def show_visualize_algorithm(algorithm_name: str, states, history, problem):
    """Generate GIF visualization for the algorithm."""
    try:
        current_file = Path(__file__).resolve()
        repo_root = current_file.parents[2] if 'tools' in str(current_file) else current_file.parents[1]
    except Exception:
        repo_root = Path.cwd() 
    
    output_dir = repo_root / 'data' / 'output' / 'visualization'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = algorithm_name.lower().replace(' ', '_').replace('-', '_')
    out_name = f'visualization-{safe_name}.gif'
    out_path = output_dir / out_name
    
    try:
        generate_gif_from_states(
            states=states,
            out_path=str(out_path),
            conflicts=history,
            duration_ms=500
        )
        print(f"GIF saved to: {out_path}")
    except Exception as e:
        tb = traceback.format_exc()
        print(f"*** ERROR generating GIF for {algorithm_name}: {e} ***\n{tb}\n")

# COMPARISON FUNCTION
def compare_algorithms(problem):
    """Run comparison of hill climbing algorithms with configurable parameters."""
    print("\n=== Algorithm Comparison ===")
    print("Configure comparison parameters:")
    
    # Get parameters from user
    num_runs = int(input("Number of runs per algorithm (default: 100): ") or "100")
    
    print("Sideways moves limits (comma-separated, default: 10,100): ", end="")
    sideways_input = input() or "10,100"
    sideways_limits = [int(x.strip()) for x in sideways_input.split(',')]
    
    random_max_moves = int(input("Max moves per restart (default: 20): ") or "20")
    random_max_restarts = int(input("Max restarts (default: 100): ") or "100")
    
    annealing_temp = float(input("Simulated annealing initial temperature (default: 400.0): ") or "400.0")
    annealing_linear_steps = int(input("Simulated annealing max steps for linear cooling (default: 1000): ") or "1000")
    annealing_exp_steps = int(input("Simulated annealing max steps for exponential cooling (default: 1000): ") or "1000")
    
    print(f"\nRunning comparison with {num_runs} runs per algorithm...")
    
    try:
        metrics = compare_hill_climbing_algorithms(
            num_runs=num_runs,
            sideways_limits=tuple(sideways_limits),
            random_max_moves=random_max_moves,
            random_max_restarts=random_max_restarts,
            annealing_temperature=annealing_temp,
            annealing_linear_max_steps=annealing_linear_steps,
            annealing_log_max_steps=annealing_exp_steps,
        )
        
        print("\n=== COMPARISON RESULTS ===")
        print_comparison_table(metrics)
        
        # Save results info
        current_file = Path(__file__).resolve()
        repo_root = current_file.parents[2] if 'tools' in str(current_file) else current_file.parents[1]
        metrics_path = repo_root / "data" / "output" / "metrics" / "metrics_hill_climbing.json"
        print(f"\nDetailed metrics saved to: {metrics_path}")
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"*** ERROR during comparison: {e} ***\n{tb}\n")

# PRINT COMPARISON TABLE
def print_comparison_table(metrics):
    """Print a formatted table of comparison metrics."""
    if not metrics:
        print("No metrics available.")
        return
    
    # Group metrics by algorithm
    algorithms = set()
    for key in metrics.keys():
        if ' avg time (ms)' in key:
            alg_name = key.replace(' avg time (ms)', '')
            algorithms.add(alg_name)
    
    algorithms = sorted(algorithms)
    
    if not algorithms:
        print("No algorithm metrics found.")
        return
    
    # Print header
    col_width = 25
    header = f"{'Metric':<{col_width}}"
    for alg in algorithms:
        header += f" | {alg:>{col_width}}"
    print(header)
    print("-" * len(header))
    
    # Print metrics
    metric_keys = [
        ('avg time (ms)', 'Average Time (ms)'),
        ('avg conflicts', 'Average Conflicts'),
        ('success count', 'Success Rate'),
        ('avg steps', 'Average Steps'),
        ('avg peak (KB)', 'Peak Memory (KB)'),
    ]
    
    for metric_suffix, display_name in metric_keys:
        row = f"{display_name:<{col_width}}"
        for alg in algorithms:
            metric_key = f"{alg} {metric_suffix}"
            value = metrics.get(metric_key, "N/A")
            row += f" | {str(value):>{col_width}}"
        print(row)
    
    print("-" * len(header))
    print()

# MAIN FUNCTION HANDLING MENU INTERACTIONS AND SEARCH EXECUTIONS
def main():
    random.seed(42)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    problem = EightQueensProblem()
    
    print("Welcome to the Eight Queens Hill Climbing Solver!")
    show_current_board(problem)

    while True:
        show_options_menu()
        option = get_option(6)

        if option == 1:
            sideways_limit = 100
            while True:
                show_algorithm_menu("sideways")
                sub_option = get_option(4)

                if sub_option == 1:
                    print("\n" + "="*60)
                    print("Running Hill Climbing with Sideways Moves Allowed...")
                    print("="*60)
                    compute_hill_climbing_with_sideways_moves(problem, sideways_limit)
                    print("="*60)
                elif sub_option == 2:
                    print("\n" + "="*60)
                    print("Visualizing Hill Climbing with Sideways Moves Allowed...")
                    print("="*60)
                    try:
                        board, history, states = hill_climbing_with_sideways_moves(
                            problem, sideways_limit, track_states=True
                        )
                        if states and len(states) > 1:
                            show_visualize_algorithm("Hill Climbing Sideways", states, history, problem)
                        else:
                            print("No state transitions to visualize.")
                    except Exception as e:
                        print(f"Error during visualization: {e}")
                    print("="*60)
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
                    print("\n" + "="*60)
                    print("Running Hill Climbing with Random Restarts...")
                    print(f"Allow sideways: {allow_sideways}, Max moves: {max_moves_per_restart}, Max restarts: {max_restarts}")
                    print("="*60)
                    compute_hill_climbing_with_random_restarts(problem, allow_sideways, max_moves_per_restart, max_restarts)
                    print("="*60)
                elif sub_option == 2:
                    print("\n" + "="*60)
                    print("Visualizing Hill Climbing with Random Restarts...")
                    print(f"Allow sideways: {allow_sideways}, Max moves: {max_moves_per_restart}, Max restarts: {max_restarts}")
                    print("="*60)
                    try:
                        board, best_fitness, restart_count, history, states = hill_climbing_with_random_restarts(
                            problem, allow_sideways, max_moves_per_restart, max_restarts, track_states=True
                        )
                        if states and len(states) > 1:
                            show_visualize_algorithm("Hill Climbing Random Restarts", states, history, problem)
                        else:
                            print("No state transitions to visualize.")
                    except Exception as e:
                        print(f"Error during visualization: {e}")
                    print("="*60)
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
            temperature = 400
            cooling_func = 2 # Default to exponential
            max_steps = 1000
            while True:
                show_algorithm_menu("simulated_annealing")
                sub_option = get_option(6)

                if sub_option == 1:
                    print("\n" + "="*60)
                    print("Running Simulated Annealing...")
                    cooling_name = 'linear' if cooling_func == 1 else 'exponential'
                    print(f"Temperature: {temperature}, Cooling: {cooling_name}, Max steps: {max_steps}")
                    print("="*60)
                    compute_simulated_annealing(problem, temperature, cooling_func, True, max_steps)
                    print("="*60)
                elif sub_option == 2:
                    print("\n" + "="*60)
                    print("Visualizing Simulated Annealing...")
                    cooling_name = 'linear' if cooling_func == 1 else 'exponential'
                    print(f"Temperature: {temperature}, Cooling: {cooling_name}, Max steps: {max_steps}")
                    print("="*60)
                    try:
                        board, fitness, history, states = simulated_annealing(
                            problem, temperature, cooling_func, track_states=True, max_steps=max_steps
                        )
                        if states and len(states) > 1:
                            show_visualize_algorithm("Simulated Annealing", states, history, problem)
                        else:
                            print("No state transitions to visualize.")
                    except Exception as e:
                        print(f"Error during visualization: {e}")
                    print("="*60)
                elif sub_option == 3:
                    temperature = int(input("Enter the initial temperature: "))
                    print(f"Initial temperature set to {temperature}.")
                elif sub_option == 4:
                    print("Enter the cooling function (linear/exponential):")
                    print("1. Linear")
                    print("2. Exponential")
                    choice = get_option(2)
                    if choice == 1:
                        cooling_func = 1  # Linear
                    elif choice == 2:
                        cooling_func = 2  # Exponential

                    print(f"Cooling function set to {'linear' if cooling_func == 1 else 'exponential'}.")
                
                elif sub_option == 5:
                    max_steps = int(input("Enter the maximum number of steps: "))
                    print(f"Max steps set to {max_steps}.")
                elif sub_option == 6:
                    break

        elif option == 4:
            print("\n" + "="*60)
            print("Comparing Algorithms...")
            print("="*60)
            compare_algorithms(problem)
            print("="*60)

        elif option == 5:
            print("Generating new random board...")
            problem = EightQueensProblem()  # This will generate a new random board
            show_current_board(problem)

        elif option == 6:
            print("Exiting the program.")
            break

# RUN THE MAIN FUNCTION
if __name__ == "__main__":
    main()