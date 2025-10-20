from typing import Any, Optional

# REPRESENTS A NODE IN THE SEARCH TREE
class Node:
    # INITIALIZES A NODE WITH STATE, COSTS, AND PARENT REFERENCE
    def __init__(self, state: Any, parent: Optional['Node'] = None,
                 action: Optional[Any] = None, g: Optional[float] = 0.0, h: Optional[float] = 0.0, f: float = 0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        self.f = f

    # RETURNS UNINFORMED COST (USED IN UNIFORM COST SEARCH)
    @property
    def f_uninformed(self) -> float:
        return self.g
    
    # RETURNS GREEDY COST (HEURISTIC ONLY)
    @property
    def f_greedy(self) -> float:
        return self.h
    
    # RETURNS A* COST (G + H)
    @property
    def f_a_star(self) -> float:
        return self.g + self.h

    # COMPARISON OPERATOR FOR PRIORITY QUEUES (BY F VALUE)
    def __lt__(self, other: 'Node') -> bool:
        return self.f < other.f

    # CHECKS IF TWO NODES REPRESENT THE SAME STATE
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.state == other.state

    # ENABLES NODE USAGE IN SETS AND DICTS
    def __hash__(self) -> int:
        return hash(self.state)
