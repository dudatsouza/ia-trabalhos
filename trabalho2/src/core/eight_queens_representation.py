# Representation: board[c] = line (0..7) of queen in column c (0..7)
from typing import List, Iterable, Tuple
import random

Board = List[int]
Move = Tuple[int, int]  # (column, new_line)

N = 8

class EightQueensProblem:
    @staticmethod
    def initial_board(r = True) -> Board:
        if not r:
            return [0, 1, 2, 3, 4, 5, 6, 7]

        # Randomly shuffle the board
        random_board = [i for i in range(N)]
        random.shuffle(random_board)

        # print("Initial board:", random_board)

        return random_board

    @staticmethod
    def conflicts(board: Board) -> int:
        # Evaluation function: number of pairs of queens in conflict.
        # If zero, then it's a solution.
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
        # Generates neighborhood moves: move the queen from one column to another row.
        # Returns valid (column, new_line) pairs.
        for col in range(N):
            for new_line in range(N):
                if new_line != board[col]:
                    yield (col, new_line)
    
    @staticmethod
    def apply(board: Board, mv: Move) -> Board:
        # Returns a new board after applying the move mv.
        c, r = mv
        newb = board.copy()
        newb[c] = r
        return newb