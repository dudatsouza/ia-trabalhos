from abc import ABC, abstractmethod
from typing import Any, Iterable, Callable, Optional

# ABSTRACT BASE CLASS THAT DEFINES THE STRUCTURE OF A SEARCH PROBLEM
class Problem(ABC):
    # RETURNS THE INITIAL STATE OF THE PROBLEM
    @property
    @abstractmethod
    def initial(self) -> Any:
        ...

    # CHECKS IF A GIVEN STATE IS A GOAL STATE
    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        ...

    # RETURNS ALL POSSIBLE ACTIONS FROM A GIVEN STATE
    @abstractmethod
    def actions(self, state: Any) -> Iterable[Any]:
        ...

    # RETURNS THE RESULTING STATE AFTER APPLYING AN ACTION
    @abstractmethod
    def result(self, state: Any, action: Any) -> Any:
        ...

    # RETURNS THE COST OF PERFORMING AN ACTION BETWEEN STATES (DEFAULT = 1)
    def action_cost(self, s: Any, a: Any, s2: Any) -> float:
        return 1.0

    # RETURNS THE HEURISTIC VALUE FOR A GIVEN STATE (DEFAULT = 0)
    def heuristic(self, s: Any, goal: Optional[Any] = None, function_h: Optional[Callable[[Any, Any], float]] = None) -> float:
        if function_h and goal is not None:
            return function_h(s, goal)
        return 0.0
