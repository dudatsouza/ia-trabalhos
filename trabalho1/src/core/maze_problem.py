from typing import Tuple, Optional, Callable
from core.problem import Problem
from core.maze_representation import Maze

Coord = Tuple[int, int]

# REPRESENTS A MAZE SEARCH PROBLEM USING THE PROBLEM BASE CLASS
class MazeProblem(Problem):
    # INITIALIZES THE MAZE PROBLEM WITH START AND GOAL POSITIONS
    def __init__(self, maze: Maze):
        self.maze = maze
        self.start = maze.start
        self.goal = maze.goal
        if self.start is None or self.goal is None:
            raise ValueError("Maze must contain 'S' and 'G'")

    # RETURNS THE INITIAL STATE OF THE PROBLEM
    @property
    def initial(self) -> Coord:
        return self.start

    # CHECKS IF THE GIVEN STATE IS THE GOAL STATE
    def is_goal(self, state: Coord) -> bool:
        return self.maze.goal_test(state)

    # RETURNS POSSIBLE ACTIONS FROM THE CURRENT STATE
    def actions(self, state: Coord):
        return self.maze.actions(state)

    # RETURNS THE RESULTING STATE AFTER AN ACTION
    def result(self, state: Coord, action: Coord) -> Coord:
        return self.maze.result(state, action)

    # RETURNS THE COST OF PERFORMING AN ACTION BETWEEN STATES
    def action_cost(self, s: Coord, a: Coord, s2: Coord) -> float:
        return self.maze.step_cost(s, a, s2)

    # COMPUTES THE HEURISTIC VALUE USING A GIVEN HEURISTIC FUNCTION
    def heuristic(self, s: Coord, goal: Optional[Coord] = None, function_h: Optional[Callable[[Coord, Coord], float]] = None) -> float:
        if function_h and goal is not None:
            return function_h(s, goal)
        return 0.0
