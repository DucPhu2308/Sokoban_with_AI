import numpy as np
from level import Level
class Gameplay:
    def __init__(self):
        self.width = 12
        self.height = 12
        self.step = 0

        self.PLAYER_SYMBOL = '@'
        self.WALL_SYMBOL = '#'
        self.BOX_SYMBOL = '$'
        self.TARGET_SYMBOL = '.'
        self.EMPTY_SYMBOL = ' '
        self.levels = Level().levels
        self.load_level(0)
        self.stackUndo = []
    def undo(self):
        if len(self.stackUndo) > 0:
            self.board = self.stackUndo.pop()
            self.step -= 1
            return True
        return False
    def load_level(self, level):
        self.board = self.levels[level].copy()
        self.step = 0
        self.targets = np.argwhere(self.levels[level] == self.TARGET_SYMBOL).tolist()
    def move_player(self, direction):
        directions = {
            "Up": (-1, 0),
            "Down": (1, 0),
            "Left": (0, -1),
            "Right": (0, 1),
            "w": (-1, 0),
            "s": (1, 0),
            "a": (0, -1),
            "d": (0, 1)
        }.get(direction)

        if not directions:
            return

        self.player_row, self.player_col = np.argwhere(self.board == self.PLAYER_SYMBOL)[0]
        new_row, new_col = self.player_row + directions[0], self.player_col + directions[1]
        next_row, next_col = new_row + directions[0], new_col + directions[1]

        if self.board[new_row][new_col] == self.EMPTY_SYMBOL or self.board[new_row][new_col] == self.TARGET_SYMBOL:
            self.stackUndo.append(self.board.copy())
            self.step += 1
            self.swap_cells(self.player_row, self.player_col, new_row, new_col)
            return True
        elif self.board[new_row][new_col] == self.BOX_SYMBOL:
            if self.board[next_row][next_col] == self.EMPTY_SYMBOL or self.board[next_row][next_col] == self.TARGET_SYMBOL:
                self.stackUndo.append(self.board.copy())
                self.step += 1
                self.swap_cells(new_row, new_col, next_row, next_col)
                self.swap_cells(self.player_row, self.player_col, new_row, new_col)
                return True
        return False
    def swap_cells(self, r1, c1, r2, c2):
        if self.board[r2][c2] == self.TARGET_SYMBOL:
            self.board[r2][c2] = self.EMPTY_SYMBOL
        self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]

        #keep track of targets
        for target in self.targets:
            if self.board[target[0]][target[1]] == self.EMPTY_SYMBOL:
                self.board[target[0]][target[1]] = self.TARGET_SYMBOL
        
    def check_win(self):
        for target in self.targets:
            if self.board[target[0]][target[1]] != self.BOX_SYMBOL:
                return False
        return True