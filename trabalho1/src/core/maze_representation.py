from typing import List, Tuple

Grid = List[List[str]]
Pos = Tuple[int, int]


# REPRESENTS THE STATE SPACE FOR THE MAZE PROBLEM
class Maze:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.H = len(grid)
        self.W = len(grid[0]) if self.H > 0 else 0
        self.start = self._find('S')
        self.goal = self._find('G')

    # FINDS THE POSITION OF A GIVEN CHARACTER IN THE GRID
    def _find(self, ch: str) -> Pos:
        for r in range(self.H):
            for c in range(self.W):
                if self.grid[r][c] == ch:
                    return (r, c)
        raise ValueError(f"Caractere '{ch}' no encontrado no grid")

    # CHECKS IF A POSITION IS WITHIN MAZE BOUNDS
    def in_bounds(self, p: Pos) -> bool:
        r, c = p
        return 0 <= r < self.H and 0 <= c < self.W

    # CHECKS IF A POSITION IS PASSABLE (NOT A WALL)
    def passable(self, p: Pos) -> bool:
        r, c = p
        return self.grid[r][c] != '#'

    # RETURNS POSSIBLE ACTIONS FROM A GIVEN POSITION
    def actions(self, p: Pos):
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

    # RETURNS THE RESULTING POSITION AFTER APPLYING AN ACTION
    def result(self, p: Pos, a: str) -> Pos:
        r, c = p
        delta = {'N':(-1,0), 'S':(1,0), 'O':(0,-1), 'L':(0,1)}
        dr, dc = delta[a]
        q = (r+dr, c+dc)
        if not (self.in_bounds(q) and self.passable(q)):
            raise ValueError('A invalida em p')
        return q

    # RETURNS THE COST OF A SINGLE STEP (DEFAULT = 1)
    def step_cost(self, p: Pos, a: str, q: Pos) -> float:
        return 1.0

    # CHECKS IF THE CURRENT POSITION IS THE GOAL
    def goal_test(self, p: Pos) -> bool:
        return p == self.goal

    # CREATES A MAZE INSTANCE FROM A TEXT FILE
    @classmethod
    def from_file(cls, file_path: str) -> 'Maze':
        with open(file_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip() != '']
        grid = [list(line) for line in lines]
        return cls(grid)

    # RETURNS NEIGHBOR COORDINATES OF A GIVEN POSITION
    def neighbors_coords(self, p: Pos):
        r, c = p
        candidates = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [q for q in candidates if self.in_bounds(q) and self.passable(q)]

    # CONVERTS THE MAZE TO AN ADJACENCY GRAPH
    def to_graph(self):
        graph = {}
        for r in range(self.H):
            for c in range(self.W):
                if self.passable((r, c)):
                    graph[(r, c)] = self.neighbors_coords((r, c))
        return graph

    # PRINTS THE MAZE IN A READABLE FORMAT
    def pretty_print(self):
        for row in self.grid:
            print(''.join(row))
