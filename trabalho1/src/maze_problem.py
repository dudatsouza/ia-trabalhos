from typing import Tuple, List, Dict, Optional
from problem import Problem

Coord = Tuple[int, int]

class MazeProblem(Problem):
    def __init__(self, matrix: List[List[str]], graph: Dict[Coord, list]):
        self.matrix = matrix
        self.graph = graph
        self.start = self._find_char('S')
        self.goal = self._find_char('G')
        if self.start is None or self.goal is None:
            raise ValueError("Maze must contain 'S' and 'G'")

    @property
    def initial(self) -> Coord:
        return self.start

    def is_goal(self, state: Coord) -> bool:
        return state == self.goal

    def actions(self, state: Coord):
        return self.graph.get(state, [])

    def result(self, state: Coord, action: Coord) -> Coord:
        return action

    def action_cost(self, s: Coord, a: Coord, s2: Coord) -> float:
        return 1.0

    def heuristic(self, s: Coord) -> float:
        return abs(s[0] - self.goal[0]) + abs(s[1] - self.goal[1])

    def _find_char(self, ch: str) -> Optional[Coord]:
        for i, row in enumerate(self.matrix):
            for j, val in enumerate(row):
                if val == ch:
                    return (i, j)
        return None