from abc import ABC, abstractmethod
from typing import Any, Iterable

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

    def heuristic(self, s: Any) -> float:
        return 0.0