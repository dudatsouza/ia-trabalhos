import math
import random
import itertools

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

def compute_simulated_annealing(problem: EightQueensProblem, temperature: int = 100, cooling_func: int = 2):
    print("Cooling function:", "Linear" if cooling_func == 1 else "Logarithmic")
    a = input("Press Enter to start the Simulated Annealing computation...")
    # CALL THE SIMULATED ANNEALING AND MEASURE TIME/MEMORY
    result, elapsed_time, memory_used, current, peak = measure_time_memory(
        simulated_annealing,
        problem,
        temperature,
        cooling_func
    )

    best_solution, best_fitness, history = result

    plot_search_history(history)

    if best_fitness is not 0:
        print("No solution found")
        print("Best solution:", best_solution)
        print("Best fitness (number of conflicts):", -best_fitness)
        return

    if best_solution:
        print("Board of Solution:", best_solution)
        print("Fitness (number of conflicts):", -best_fitness)
        print(f"Time taken: {elapsed_time:.3f} milliseconds")
        print(f"Memory used: {memory_used:.12f} B")
        print(f"Current memory usage: {current / 1024:.3f} KB; Peak: {peak / 1024:.3f} KB")


def simulated_annealing(problem, temperature=100, cooling_func=2):
    random.seed(42)
    current = problem.initial_board()
    history = []
    for t in itertools.count(start=1):
        history.append(-problem.fitness(current))
        T = schedule(t, cooling_func=cooling_func, initial_temp=temperature)
        print( f"Temperature at step {t}: {T}" )
        if T == 0:
            return current, problem.fitness(current), history
        
        lista = [problem.apply(current, mv) for mv in problem.neighbors(current)]

        next = random.choice(lista)

        delta_E = problem.conflicts(current) - problem.conflicts(next)

        if delta_E > 0:
            current = next
        else:
            probability = math.exp(-delta_E / T)
            if random.random() < probability:
                current = next
    return current, problem.fitness(current), history


def schedule(t, cooling_func=2, initial_temp=100):
    print( f"Scheduling at time {t} with cooling function {cooling_func} and initial temp {initial_temp}" )
    if cooling_func == 1:
        val = initial_temp - 0.1 * t # Linear cooling
        return val if val > 0 else 0  
    elif cooling_func == 2:
        val = initial_temp / math.log(t + 1) # Logarithmic cooling
        if val - 0.1 < 10:
            return 0
        return val