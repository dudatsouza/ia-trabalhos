from typing import Tuple, Optional, Callable
from problem import Problem
from maze_representation import Maze

Coord = Tuple[int, int]


class MazeProblem(Problem):
    def __init__(self, maze: Maze):
        self.maze = maze
        self.start = maze.start
        self.goal = maze.goal
        if self.start is None or self.goal is None:
            raise ValueError("Maze must contain 'S' and 'G'")

    @property
    def initial(self) -> Coord:
        return self.start

    def is_goal(self, state: Coord) -> bool:
        return self.maze.goal_test(state)

    def actions(self, state: Coord):
        return self.maze.actions(state)

    def result(self, state: Coord, action: Coord) -> Coord:
        # In our Maze representation an action is a direction; use maze.result
        return self.maze.result(state, action)

    def action_cost(self, s: Coord, a: Coord, s2: Coord) -> float:
        return self.maze.step_cost(s, a, s2)

    def heuristic(self, s: Coord, o: Coord, function_h: Optional[Callable[[Coord, Coord], float]] = None) -> float:
        if function_h:
            return function_h(s, o)

        return 0