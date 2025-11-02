from core.eight_queens_representation import EightQueensProblem

from tools.measure_time_memory import measure_time_memory

import matplotlib.pyplot as plt
import random

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

    if best_solution:
        for i in range(8):
            for j in range(8):
                if best_solution and best_solution[j] == i:
                    print("Q", end=' ')
                else:
                    for mv in problem.neighbors(best_solution):
                        if mv[0] == j and mv[1] == i:
                            print(f"{problem.conflicts(problem.apply(best_solution, mv))}", end=' ')
            print()

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
    random.seed(123)
    current = problem.initial_board()
    sideways_moves = 0
    history = []
    # Keep at most 8 visited boards
    visited_boards = {}

    while True:
        history.append(-problem.fitness(current))

        neighbor = current
        best_value = float('-inf')
        
        for mv in problem.neighbors(current):
            n = problem.apply(current, mv)

            if visited_boards is not None and tuple(n) in visited_boards:
                continue

            if problem.fitness(n) > best_value:
                best_value = problem.fitness(n)
                neighbor = n

        if problem.fitness(neighbor) > problem.fitness(current):
            # If the size exceeds 8, remove the oldest entry
            if len(visited_boards) >= 8:
                oldest_board = next(iter(visited_boards))
                del visited_boards[oldest_board]

            visited_boards[tuple(current)] = problem.conflicts(current)
            current = neighbor
            sideways_moves = 0
        elif problem.fitness(neighbor) == problem.fitness(current):
            if sideways_moves < max_sideways_moves:
                if len(visited_boards) >= 8:
                    oldest_board = next(iter(visited_boards))
                    del visited_boards[oldest_board]
                visited_boards[tuple(current)] = problem.conflicts(current)
                current = neighbor
                sideways_moves += 1
            else:
                break
        else:
            break

    return current, history