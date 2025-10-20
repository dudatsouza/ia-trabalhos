from typing import Tuple

Pos = Tuple[int, int]

# MANHATTAN DISTANCE HEURISTIC (4-DIRECTIONAL MOVEMENT)
def h_manhattan_distance(a: Pos, b: Pos) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# EUCLIDEAN DISTANCE HEURISTIC (STRAIGHT-LINE DISTANCE)
def h_euclidean_distance(a: Pos, b: Pos) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# OCTILE DISTANCE HEURISTIC (DIAGONAL + STRAIGHT MOVES)
def h_octile_distance(a: Pos, b: Pos) -> float:
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (2**0.5 - 1) * min(dx, dy)

# CHEBYSHEV DISTANCE HEURISTIC (8-DIRECTIONAL UNIFORM COST)
def h_chebyshev_distance(a: Pos, b: Pos) -> float:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
