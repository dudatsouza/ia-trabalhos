from abc import ABC, abstractmethod
from typing import Any, Iterable, Callable, Optional

class Problem(ABC):
    @property
    @abstractmethod
    def initial(self) -> Any:
        ...

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        ...

    @abstractmethod
    def actions(self, state: Any) -> Iterable[Any]:
        ...

    @abstractmethod
    def result(self, state: Any, action: Any) -> Any:
        ...

    def action_cost(self, s: Any, a: Any, s2: Any) -> float:
        return 1.0

    def heuristic(self, s: Any, goal: Optional[Any] = None, function_h: Optional[Callable[[Any, Any], float]] = None) -> float:
        """Return heuristic value for state s. Subclasses can override. Default is 0.

        Signature accepts optional goal and a function to compute heuristic for compatibility.
        """
        if function_h and goal is not None:
            return function_h(s, goal)
        return 0.0
