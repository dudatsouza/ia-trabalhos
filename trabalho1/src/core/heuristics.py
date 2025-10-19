from typing import Tuple
Pos = Tuple[int, int]

def h_manhattan_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Manhattan entre dois pontos a e b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def h_euclidean_distance(a: Pos, b: Pos) -> float:
    """Heurística da distância Euclidiana entre dois pontos a e b."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
