from typing import List, Optional


def hill_climbing(problem, track_states: bool = False):
    """Classical hill climbing that optionally records visited boards."""

    current = problem.initial_board()
    history: List[int] = [problem.conflicts(current)]
    states: Optional[List[List[int]]] = [current.copy()] if track_states else None

    while True:
        neighbor = current
        best_value = float('-inf')

        for mv in problem.neighbors(current):
            candidate = problem.apply(current, mv)
            fitness = problem.fitness(candidate)
            if fitness > best_value:
                best_value = fitness
                neighbor = candidate

        if problem.fitness(neighbor) <= problem.fitness(current):
            return current, history, states if track_states else None

        current = neighbor
        history.append(problem.conflicts(current))
        if track_states and states is not None:
            states.append(current.copy())