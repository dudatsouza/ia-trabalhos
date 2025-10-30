def hill_climbing(problem):
    current = problem.initial_board()
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

        if problem.fitness(neighbor) <= problem.fitness(current):
            return current, history
        
        current = neighbor