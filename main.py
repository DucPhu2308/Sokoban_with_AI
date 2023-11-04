import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import numpy as np
from gameplay import Gameplay
import copy
from collections import deque
import time

class Sokoban:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.root.title("8-puzzle")

        self.TILE_SIZE = 50
        self.load_images()

        self.gameplay = Gameplay()
        self.initializeComponents()
        self.draw_board(self.gameplay.board)

        self.root.bind("<Key>", self.move_player)
    def initializeComponents(self):
        #game frame
        self.canvas = tk.Canvas(self.root, width=self.gameplay.width * self.TILE_SIZE, 
                                height=self.gameplay.height * self.TILE_SIZE, background="white")
        self.canvas.place(x=350, y=120)

        #title and step label
        self.title = tk.Label(self.root, text="Sokoban", font=("Arial", 30, "bold"))
        self.title.place(x=560, y=20)
        self.stepLabel = tk.Label(self.root, text=f"Step: 0", font=("Arial", 20))
        self.stepLabel.place(x=350, y=75)
        self.visitedLabel = tk.Label(self.root, text=f"Visited: 0", font=("Arial", 20))
        self.visitedLabel.place(x=500, y=75)

        #button frame
        self.btnFrame = tk.Frame(self.root, width=200, height=500, background="cyan")
        self.btnFrame.place(x=100, y=120)
        self.btnFrame.pack_propagate(0) # don't shrink
        BUTTON_WIDTH = 10
        PADDING = 15
        #combobox for algorithm
        cbAlgo = ttk.Combobox(self.btnFrame, values=["BFS", "DFS", "IDS", "UCS", "Greedy","A*"], font=("Arial", 20), 
                              width=BUTTON_WIDTH, state="readonly")
        # stop control with up and down arrow keys
        cbAlgo.bind("<<ComboboxSelected>>", lambda event: self.root.focus_set())
        cbAlgo.current(0)
        cbAlgo.pack(pady=PADDING)
        btnSolve = tk.Button(self.btnFrame, text="Solve", font=("Arial", 20), 
                     width=BUTTON_WIDTH, command=lambda: self.solve(cbAlgo.get()))
        btnSolve.pack(pady=PADDING)
        #combobox for level
        cbLevel = ttk.Combobox(self.btnFrame, values=[f"Level {i}" for i in range(len(self.gameplay.levels))], font=("Arial", 20), 
                              width=BUTTON_WIDTH, state="readonly")
        # stop control with up and down arrow keys
        cbLevel.bind("<<ComboboxSelected>>", lambda event: self.root.focus_set())
        cbLevel.current(0)
        cbLevel.pack(pady=PADDING)
        btnLoad = tk.Button(self.btnFrame, text="Load level", font=("Arial", 20), 
                     width=BUTTON_WIDTH, command=lambda: self.load_level(cbLevel.current()))
        btnLoad.pack(pady=PADDING)
    def load_level(self, level):
        self.gameplay.load_level(level)
        print(self.gameplay.board)
        self.stepLabel.config(text=f"Step: 0")
        self.draw_board(self.gameplay.board)
    def solve(self, choice):
        if choice == "BFS":
            self.solveBFS()
        elif choice == "DFS":
            self.solveDFS(self.state)
        elif choice == "IDS":
            self.solveIDS(self.state)
        elif choice == "UCS":
            self.solveUCS(self.state)
        elif choice == "Greedy":
            self.solveGreedy(self.state)
        elif choice == "A*":
            self.solveAStar(self.state)
    def solveBFS(self):
        visited = set()
        queue = deque([(self.gameplay, [])])
        visited.add(tuple(self.gameplay.board.flatten()))

        while queue:
            current_gameplay, path = queue.popleft()

            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True

            for new_gameplay, move in self.getChildren(current_gameplay):
                if tuple(new_gameplay.board.flatten()) not in visited:
                    visited.add(tuple(new_gameplay.board.flatten()))
                    queue.append((new_gameplay, path + [move]))
        return False
    def animateSolution(self, path):
        for move in path:
            self.gameplay.move_player(move)
            self.stepLabel.config(text=f"Step: {self.gameplay.step}")
            self.draw_board(self.gameplay.board)
            self.root.update()
            time.sleep(0.2)
    def getChildren(self, gameplay):
        directions = ["Up", "Down", "Left", "Right"]
        children = []
        for direction in directions:
            new_state = copy.deepcopy(gameplay)
            if new_state.move_player(direction):
                children.append((new_state, direction))
        return children
            
    def load_images(self):
        player_image = Image.open("images/player.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.player_image = ImageTk.PhotoImage(player_image)

        box_image = Image.open("images/box.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.box_image = ImageTk.PhotoImage(box_image)

        wall_image = Image.open("images/wall.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.wall_image = ImageTk.PhotoImage(wall_image)

        empty_image = Image.open("images/grass.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.empty_image = ImageTk.PhotoImage(empty_image)

        target_image = Image.open("images/target.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.target_image = ImageTk.PhotoImage(target_image)

    def move_player(self, event):
        directions = ["Up", "Down", "Left", "Right"]
        if event.keysym not in directions:
            return
        if self.gameplay.move_player(event.keysym):
            self.stepLabel.config(text=f"Step: {self.gameplay.step}")
            self.draw_board(self.gameplay.board)
            if self.gameplay.check_win():
                messagebox.showinfo("Congratulation", "You win!")
    def draw_board(self, board):
        self.canvas.delete("all")
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                x, y = j * 50, i * 50
                if cell == self.gameplay.WALL_SYMBOL:
                    self.canvas.create_image(x+25, y+25, image=self.wall_image)
                elif cell == self.gameplay.EMPTY_SYMBOL:
                    self.canvas.create_image(x+25,y+25, image=self.empty_image)
                elif cell == self.gameplay.BOX_SYMBOL:
                    if [i, j] in self.gameplay.targets:
                        self.canvas.create_image(x+25, y+25, image=self.box_image)
                    else:
                        self.canvas.create_image(x+25, y+25, image=self.box_image)
                elif cell == self.gameplay.TARGET_SYMBOL:
                    self.canvas.create_image(x+25,y+25, image=self.empty_image)
                    self.canvas.create_oval(x+20, y+20, x+30, y+30, fill='red')
                elif cell == self.gameplay.PLAYER_SYMBOL:
                    self.canvas.create_image(x+25, y+25, image=self.player_image)

if __name__ == "__main__":
    root = tk.Tk()
    game = Sokoban(root)
    root.mainloop()