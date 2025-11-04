# IMPORTS EXTERNAL
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Sequence, Tuple
from pathlib import Path

# IMPORTS INTERNAL
# CORE
from core.eight_queens_representation import EightQueensProblem
# TOOLS
from tools.measure_time_memory import measure_time_memory

# PLOT THE NUMBER OF CONFLICTS OVER ITERATIONS
def plot_search_history(history: List[int], specification: int) -> None:
    if not history:
        print("No history to plot.")
        return
    
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "data" / "output" / "graphics" / "progress"

    plt.figure(figsize=(10, 6))
    plt.plot(history, marker='o', linestyle='-', markersize=4)
    plt.title(f"Hill Climbing Search Progress - Sideways Moves - {specification}")
    plt.xlabel("Iteration")
    plt.ylabel("Number of Conflicts")
    plt.grid(True)
    # ADD A HORIZONTAL LINE AT 0 TO REPRESENT THE GOAL
    plt.axhline(y=0, color='r', linestyle='--', label='Goal (0 Conflicts)')
    plt.legend()
    plt.savefig(out_dir / f"progress-sideways-{specification}.png", dpi=160)
    plt.show()

# COMPUTE HILL CLIMBING WITH SIDEWAYS MOVES AND PRINT METRICS
def compute_hill_climbing_with_sideways_moves(
    problem: EightQueensProblem,
    max_sideways_moves: int = 100,
    track_states: bool = True,
    initial_board: Optional[Sequence[int]] = None,
):
    
    result, elapsed_time, memory_used, current_mem, peak_mem = measure_time_memory(
        hill_climbing_with_sideways_moves,
        problem,
        max_sideways_moves,
        track_states=track_states,
        initial_board=initial_board,
    )

    best_solution, history, states = result

    # PLOT THE SEARCH HISTORY
    plot_search_history(history, max_sideways_moves)

    if best_solution:
        for i in range(8):
            for j in range(8):
                if best_solution[j] == i:
                    print("Q", end=" ")
                else:
                    for mv in problem.neighbors(best_solution):
                        if mv[0] == j and mv[1] == i:
                            print(f"{problem.conflicts(problem.apply(best_solution, mv))}", end=" ")
            print()

    if best_solution is None or problem.fitness(best_solution) != 0:
        print("No solution found")
        print("Board of Best solution:", best_solution)
        print(
            "Best fitness (number of conflicts):",
            -problem.fitness(best_solution) if best_solution else 0,
        )
    else:
        print("Board of Solution:", best_solution)
        print(
            "Fitness (number of conflicts):",
            -problem.fitness(best_solution) if best_solution else 0,
        )
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(
            f"Current memory usage: {current_mem / 1024:.3f} KB; Peak: {peak_mem / 1024:.3f} KB"
        )

    return {
        "solution": best_solution,
        "history": history,
        "states": states,
        "elapsed_ms": elapsed_time,
        "rss_delta": memory_used,
        "current_bytes": current_mem,
        "peak_bytes": peak_mem,
    }

# HILL CLIMBING WITH SIDEWAYS MOVES IMPLEMENTATION
def hill_climbing_with_sideways_moves(
    problem,
    max_sideways_moves: int,
    track_states: bool = False,
    initial_board: Optional[Sequence[int]] = None,
):
    current = list(initial_board) if initial_board is not None else problem.initial_board()
    sideways_moves = 0
    history: List[int] = [problem.conflicts(current)]
    states: Optional[List[List[int]]] = [current.copy()] if track_states else None
    visited_boards: Dict[Tuple[int, ...], int] = {}

    while True:
        neighbor = current
        best_value = float("-inf")

        for mv in problem.neighbors(current):
            candidate = problem.apply(current, mv)

            if tuple(candidate) in visited_boards:
                continue

            fitness = problem.fitness(candidate)
            if fitness > best_value:
                best_value = fitness
                neighbor = candidate

        if neighbor is current:
            break

        current_fitness = problem.fitness(current)
        neighbor_fitness = problem.fitness(neighbor)

        if neighbor_fitness > current_fitness:
            if len(visited_boards) >= 8:
                oldest_board = next(iter(visited_boards))
                del visited_boards[oldest_board]

            visited_boards[tuple(current)] = problem.conflicts(current)
            current = neighbor
            sideways_moves = 0
            history.append(problem.conflicts(current))
            if track_states and states is not None:
                states.append(current.copy())

        elif neighbor_fitness == current_fitness:
            if sideways_moves < max_sideways_moves:
                if len(visited_boards) >= 8:
                    oldest_board = next(iter(visited_boards))
                    del visited_boards[oldest_board]

                visited_boards[tuple(current)] = problem.conflicts(current)
                current = neighbor
                sideways_moves += 1
                history.append(problem.conflicts(current))
                if track_states and states is not None:
                    states.append(current.copy())
            else:
                break
        else:
            break

    return current, history, states if track_states else None