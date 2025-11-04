# IMPORTS EXTERNAL
from typing import List, Iterable, Tuple
import random

# TYPE ALIASES
Board = List[int]
Move = Tuple[int, int]  # (column, new_line)

# EIGHT QUEENS PROBLEM REPRESENTATION
N = 8

class EightQueensProblem:
    @staticmethod
    def initial_board(r = True) -> Board:
        if not r:
            return [0, 1, 2, 3, 4, 5, 6, 7]
        # RANDOMLY SHUFFLED THE BOARD
        random_board = [i for i in range(N)]
        random.shuffle(random_board)

        # print("Initial board:", random_board)

        return random_board

    @staticmethod
    def conflicts(board: Board) -> int:
        # EVALUATION FUNCTION: NUMBER OF PAIRS OF QUEENS IN CONFLICT. (If zero, then it's a solution.)
        conflict_count = 0
        for c1 in range(N):
            for c2 in range(c1 + 1, N):
                if board[c1] == board[c2] or abs(board[c1] - board[c2]) == abs(c1 - c2):
                    conflict_count += 1

        return conflict_count

    @staticmethod
    def fitness(board: Board) -> int:
        return -EightQueensProblem.conflicts(board)

    @staticmethod
    def neighbors(board: Board) -> Iterable[Move]:
        # GENERATES NEIGHBORHOOD MOVES: MOVE THE QUEEN FROM ONE COLUMN TO ANOTHER ROW. (Returns valid (column, new_line) pairs.)
        for col in range(N):
            for new_line in range(N):
                if new_line != board[col]:
                    yield (col, new_line)
    
    @staticmethod
    def apply(board: Board, mv: Move) -> Board:
        # RETURNS A NEW BOARD AFTER APPLYING THE MOVE MV.
        c, r = mv
        newb = board.copy()
        newb[c] = r
        return newb