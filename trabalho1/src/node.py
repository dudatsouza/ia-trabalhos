from typing import Any, Optional

class Node:
    def __init__(self, state: Any, parent: Optional['Node'] = None,
                 action: Optional[Any] = None, g: float = 0.0, h: Optional[float] = 0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h

    @property
    def f(self) -> float:
        return self.g + self.h

    def __lt__(self, other: 'Node') -> bool:
        return self.f < other.f

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self) -> int:
        return hash(self.state)