from core.eight_queens_representation import EightQueensProblem

from tools.measure_time_memory import measure_time_memory

from greedy_local_search.sideways_moves import hill_climbing_with_sideways_moves
from greedy_local_search.hill_climbing import hill_climbing

import matplotlib.pyplot as plt

def plot_search_history(history):
    """Plots the number of conflicts over iterations."""
    if not history:
        print("No history to plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(history, marker='o', linestyle='-', markersize=4)
    plt.title("Hill Climbing Search Progress")
    plt.xlabel("Iteration")
    plt.ylabel("Number of Conflicts")
    plt.grid(True)
    # Add a horizontal line at 0 to represent the goal
    plt.axhline(y=0, color='r', linestyle='--', label='Goal (0 Conflicts)')
    plt.legend()
    plt.show()

def compute_hill_climbing_with_random_restarts(problem: EightQueensProblem, allow_sideways: bool = False, max_moves_per_restart: int = 100, max_restarts: int = 1000):
    # CALL THE HILL CLIMBING WITH RANDOM RESTARTS AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        hill_climbing_with_random_restarts,
        problem,
        allow_sideways,
        max_moves_per_restart,
        max_restarts
    )

    best_solution, best_fitness, restart_count, history = result

    plot_search_history(history)

    if best_fitness is not 0:
        print("No solution found")
        print("Best solution:", best_solution)
        print("Best fitness (number of conflicts):", -best_fitness)
        print("Number of restarts:", restart_count)
        return

    if best_solution:
        print("Board of Solution:", best_solution)
        print("Fitness (number of conflicts):", -best_fitness)
        print("Number of restarts:", restart_count)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")


def hill_climbing_with_random_restarts(problem, allow_sideways=False, max_moves_per_restart=100, max_restarts=1000):
    best_solution = None
    best_fitness = float('-inf')
    restart_count = 0

    for restart in range(max_restarts):
        restart_count += 1

        if allow_sideways:
            current, history = hill_climbing_with_sideways_moves(problem, max_moves_per_restart)
        else:
            current, history = hill_climbing(problem)

        current_fitness = problem.fitness(current)
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_solution = current

        if best_fitness == 0:  # Found a solution with zero conflicts
            break

    return best_solution, best_fitness, restart_count, history