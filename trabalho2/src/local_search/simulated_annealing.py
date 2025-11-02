import math
import random
from typing import List, Optional, Sequence

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

def compute_simulated_annealing(
    problem: EightQueensProblem,
    temperature: int = 100,
    cooling_func: int = 1,
    track_states: bool = True,
    max_steps: int = 1000,
    initial_board: Optional[Sequence[int]] = None,
    rng: Optional[random.Random] = None,
):
    print("Cooling function:", "Linear" if cooling_func == 1 else "Logarithmic")
    a = input("Press Enter to start the Simulated Annealing computation...")
    # CALL THE SIMULATED ANNEALING AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        simulated_annealing,
        problem,
        temperature,
        cooling_func,
        track_states,
        max_steps,
        initial_board=initial_board,
        rng=rng,
    )

    best_solution, best_fitness, history, states = result

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
        return {
            "solution": best_solution,
            "history": history,
            "states": states,
            "fitness": best_fitness,
            "elapsed_ms": elapsed_time,
            "rss_delta": memory_used,
            "current_bytes": current,
            "peak_bytes": peak,
        }

    if best_solution:
        print("Board of Solution:", best_solution)
        print("Fitness (number of conflicts):", -best_fitness)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")

    return {
        "solution": best_solution,
        "history": history,
        "states": states,
        "fitness": best_fitness,
        "elapsed_ms": elapsed_time,
        "rss_delta": memory_used,
        "current_bytes": current,
        "peak_bytes": peak,
    }


def simulated_annealing(
    problem,
    temperature,
    cooling_func,
    track_states,
    max_steps,
    initial_board: Optional[Sequence[int]] = None,
    rng: Optional[random.Random] = None,
):
    generator = rng or random.Random()
    current = list(initial_board) if initial_board is not None else problem.initial_board()
    history: List[int] = [problem.conflicts(current)]
    states: Optional[List[List[int]]] = [current.copy()] if track_states else None

    for t in range(max_steps):
        T = schedule(t, cooling_func=cooling_func, initial_temp=temperature, max_steps=max_steps)
        if T <= 0:
            break

        neighbors = [problem.apply(current, mv) for mv in problem.neighbors(current)]
        candidate = generator.choice(neighbors)

        current_conflicts = problem.conflicts(current)
        candidate_conflicts = problem.conflicts(candidate)
        delta_conflicts = current_conflicts - candidate_conflicts

        if delta_conflicts > 0:
            current = candidate
        else:
            acceptance = math.exp(delta_conflicts / T)
            r = generator.random()
            if r < acceptance:
                current = candidate

        history.append(problem.conflicts(current))
        if track_states and states is not None:
            states.append(current.copy())

    return current, problem.fitness(current), history, states if track_states else None


def schedule(t, cooling_func, initial_temp=100, max_steps=1000):
    # print( f"Scheduling at time {t} with cooling function {cooling_func} and initial temp {initial_temp}" )
    if cooling_func == 1:
        val = 1 - ((t+1)  / max_steps) # Linear cooling
        # print ( f"Linear cooling value at time {t}: {val}" )
        return val if val > 0 else 0  
    elif cooling_func == 2:
        val = initial_temp / math.log(t + 10) # Logarithmic cooling
        # print( f"Logarithmic cooling value at time {t}: {val}" )
        return val if (val - 10) > 0 else 0