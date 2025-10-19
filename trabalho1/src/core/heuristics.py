from typing import Tuple
Pos = Tuple[int, int]

def h_manhattan_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Manhattan entre dois pontos a e b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def h_euclidean_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Euclidiana entre dois pontos a e b."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def h_octile_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Octile entre dois pontos a e b."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (2**0.5 - 1) * min(dx, dy)

def h_chebyshev_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Chebyshev entre dois pontos a e b."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))