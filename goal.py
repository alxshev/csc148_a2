"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple, Any
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    # Assures independent colours chosen
    cols = random.sample(COLOUR_LIST, num_goals)
    if random.randint(0, 1) > .5:
        return [PerimeterGoal(random.choice(col)) for col in cols]
    return [BlobGoal(random.choice(col)) for col in cols]


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    d = 2 ** (block.max_depth - block.level)
    if not block.children:
        return [[block.colour] * d] * d
    return _merge([_flatten(c) for c in block.children])


def _merge(block_lists: List[List[int]]) -> List[int]:
    """Merges 4 nxn lists into one 2nx2n list. Order of sublists in
    <block_lists> is (Top-Right, TL, BL, BR)
    A B C D represents TL, TR, BL, BR sections of block"""
    B, A, C, D = block_lists
    n = len(A)
    return [A[i] + C[i] for i in range(n)] + [B[i] + D[i] for i in range(n)]

class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    def score(self, board: Block) -> int:
        grid = _flatten(board)
        col = self.colour
        counter = 0
        for i in range(len(grid)):
            counter += (grid[0][i] == col) + (grid[-1][i] == col) + (grid[i][0] == col) + (grid[i][-1] == col)
        return counter

    def description(self) -> str:
        """Return a description of perimeter goal."""
        return "Perimeter: put as many of your colour on the perimeter!"


class BlobGoal(Goal):
    def score(self, board: Block) -> int:
        bd = _flatten(board)
        d = len(bd)
        visited = [[-1 for i in range(d)] for j in range(d)]
        return max(self._undiscovered_blob_size((i, j), bd, visited) for i in range(d) for j in range(d))

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        d = len(board)
        i, j = pos
        if not (0 <= i < d and 0 <= j < d) or visited[i][j] != -1:
            return 0
        visited[i][j] = int(board[i][j] == self.colour)
        next_steps = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
        return 0 if visited[i][j] == 0 else 1 + sum(self._undiscovered_blob_size(x, board, visited) for x in next_steps)

    def description(self) -> str:
        """return a description of blob goal."""
        return "Blob Goal: aim for largest blob of your given colour!"


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
