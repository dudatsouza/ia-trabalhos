from core.eight_queens_representation import EightQueensProblem

from tools.measure_time_memory import measure_time_memory

from greedy_local_search.sideways_moves import hill_climbing_with_sideways_moves
from greedy_local_search.hill_climbing import hill_climbing

import matplotlib.pyplot as plt
from typing import List, Optional

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

def compute_hill_climbing_with_random_restarts(
    problem: EightQueensProblem,
    allow_sideways: bool = False,
    max_moves_per_restart: int = 100,
    max_restarts: int = 100,
    track_states: bool = True,
):
    # CALL THE HILL CLIMBING WITH RANDOM RESTARTS AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        hill_climbing_with_random_restarts,
        problem,
        allow_sideways,
        max_moves_per_restart,
        max_restarts,
        track_states,
    )

    best_solution, best_fitness, restart_count, history, states = result

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

    if best_fitness != 0:
        print("No solution found")
        print("Best solution:", best_solution)
        print("Best fitness (number of conflicts):", -best_fitness)
        print("Number of restarts:", restart_count)
        return {
            "solution": best_solution,
            "history": history,
            "states": states,
            "best_fitness": best_fitness,
            "restart_count": restart_count,
            "elapsed_ms": elapsed_time,
            "rss_delta": memory_used,
            "current_bytes": current,
            "peak_bytes": peak,
        }

    if best_solution:
        print("Board of Solution:", best_solution)
        print("Fitness (number of conflicts):", -best_fitness)
        print("Number of restarts:", restart_count)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

    return {
        "solution": best_solution,
        "history": history,
        "states": states,
        "best_fitness": best_fitness,
        "restart_count": restart_count,
        "elapsed_ms": elapsed_time,
        "rss_delta": memory_used,
        "current_bytes": current,
        "peak_bytes": peak,
    }


def hill_climbing_with_random_restarts(
    problem,
    allow_sideways: bool = False,
    max_moves_per_restart: int = 100,
    max_restarts: int = 100,
    track_states: bool = False,
):
    best_solution = None
    best_fitness = float('-inf')
    restart_count = 0
    best_history: List[int] = []
    best_states: Optional[List[List[int]]] = None

    for restart in range(max_restarts):
        restart_count += 1

        if allow_sideways:
            current, history, states = hill_climbing_with_sideways_moves(
                problem,
                max_moves_per_restart,
                track_states=track_states,
            )
        else:
            current, history, states = hill_climbing(
                problem,
                track_states=track_states,
            )

        current_fitness = problem.fitness(current)
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_solution = current
            best_history = history
            best_states = states

        if best_fitness == 0:  # Found a solution with zero conflicts
            break

    return (
        best_solution,
        best_fitness,
        restart_count,
        best_history,
        best_states if track_states else None,
    )