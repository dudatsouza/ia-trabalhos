from core.eight_queens_representation import EightQueensProblem

from tools.measure_time_memory import measure_time_memory

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

def compute_hill_climbing_with_sideways_moves(problem: EightQueensProblem, max_sideways_moves: int = 100):
    # CALL THE HILL CLIMBING WITH SIDEWAYS MOVES AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        hill_climbing_with_sideways_moves,
        problem,
        max_sideways_moves
    )

    best_solution, history = result

    plot_search_history(history)

    if best_solution is None or problem.fitness(best_solution) != 0:
        print("No solution found")
        print("Board of Best solution:", best_solution)
        print("Best fitness (number of conflicts):", -problem.fitness(best_solution) if best_solution else 0)
        return
    

    if best_solution:
        print("Board of Solution:", best_solution)
        print("Fitness (number of conflicts):", -problem.fitness(best_solution) if best_solution else 0)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

def hill_climbing_with_sideways_moves(problem, max_sideways_moves):
    current = problem.initial_board()
    sideways_moves = 0
    history = []

    while True:
        history.append(-problem.fitness(current))

        neighbor = current
        best_value = 0
        for mv in problem.neighbors(current):
            n = problem.apply(current, mv)
            if problem.fitness(n) > best_value:
                best_value = problem.fitness(n)
                neighbor = n

        if problem.fitness(neighbor) > problem.fitness(current):
            current = neighbor
            sideways_moves = 0
        elif problem.fitness(neighbor) == problem.fitness(current):
            if sideways_moves < max_sideways_moves:
                current = neighbor
                sideways_moves += 1
            else:
                break
        else:
            break

    return current, history