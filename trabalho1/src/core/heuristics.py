from typing import Tuple

Pos = Tuple[int, int]

# MANHATTAN DISTANCE HEURISTIC (4-DIRECTIONAL MOVEMENT)
def h_manhattan_distance(a: Pos, b: Pos) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# EUCLIDEAN DISTANCE HEURISTIC (STRAIGHT-LINE DISTANCE)
def h_euclidean_distance(a: Pos, b: Pos) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

# INADMISSIBLE HEURISTIC (2 / MANHATTAN DISTANCE)
def h_inadmissible(a: Pos, b: Pos) -> float:
    return 2/h_manhattan_distance(a, b) if h_manhattan_distance(a, b) != 0 else 0