from typing import List, Tuple

Grid = List[List[str]]
Pos = Tuple[int, int]


class Maze:
    """Representa o espaço de estados para o problema do labirinto.

    Convenções:
     - 'S' = início, 'G' = objetivo, '#' = parede, '.' = célula livre.
     - Ações: mover para N, S, O, L (4-direções). Expandir para 8-direções se desejado.
    """

    def __init__(self, grid: Grid):
        self.grid = grid
        self.H = len(grid)
        self.W = len(grid[0]) if self.H > 0 else 0
        self.start = self._find('S')
        self.goal = self._find('G')

    def _find(self, ch: str) -> Pos:
        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r][c] == ch:
                    return (r, c)
        raise ValueError(f"Caractere '{ch}' não encontrado no grid")

    def in_bounds(self, p: Pos) -> bool:
        r, c = p
        return 0 <= r < self.H and 0 <= c < self.W

    def passable(self, p: Pos) -> bool:
        r, c = p
        return self.grid[r][c] != '#'

    def actions(self, p: Pos):
        """Retorna a lista de ações válidas em p. Ex.: ['N','S','O','L']"""
        acts = []
        r, c = p
        candidates = {
            'N': (r-1, c),
            'S': (r+1, c),
            'O': (r, c-1),
            'L': (r, c+1),
        }

        for a, q in candidates.items():
            if self.in_bounds(q) and self.passable(q):
                acts.append(a)
        return acts

    def result(self, p: Pos, a: str) -> Pos:
        """Função de transição T(p,a)."""
        r, c = p
        delta = {'N':(-1,0), 'S':(1,0), 'O':(0,-1), 'L':(0,1)}
        dr, dc = delta[a]
        q = (r+dr, c+dc)
        if not (self.in_bounds(q) and self.passable(q)):
            raise ValueError('Ação inválida em p')
        return q

    def step_cost(self, p: Pos, a: str, q: Pos) -> float:
        """Custo de passo. Por padrão, custo unitário."""
        return 1.0

    def goal_test(self, p: Pos) -> bool:
        return p == self.goal

    # --- Additional helpers (safe to add) ---------------------------------
    @classmethod
    def from_file(cls, file_path: str) -> 'Maze':
        """Create a Maze instance from a text file (lines of chars)."""
        with open(file_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip() != '']
        grid = [list(line) for line in lines]
        return cls(grid)

    def neighbors_coords(self, p: Pos):
        """Return list of neighbor coordinates (instead of direction labels)."""
        r, c = p
        candidates = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [q for q in candidates if self.in_bounds(q) and self.passable(q)]

    def to_graph(self):
        """Return adjacency dict mapping (r,c) -> list[(r,c)] for walkable cells."""
        graph = {}
        for r in range(self.H):
            for c in range(self.W):
                if self.passable((r, c)):
                    graph[(r, c)] = self.neighbors_coords((r, c))
        return graph

    def pretty_print(self):
        for row in self.grid:
            print(''.join(row))

