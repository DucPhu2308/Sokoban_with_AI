import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import ImageTk, Image
import numpy as np
from gameplay import Gameplay
import copy
from collections import deque
from queue import PriorityQueue
import time

class Sokoban:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.root.title("Sokoban")
        bg_image = Image.open("images/bg.png").resize((1280, 720))
        self.bg_image = ImageTk.PhotoImage(bg_image)
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=0, y=0)
        self.TILE_SIZE = 50
        self.load_images()

        self.gameplay = Gameplay()
        self.initializeComponents()
        self.draw_board(self.gameplay.board)

        self.root.bind("<Key>", self.move_player)
    
    def initializeComponents(self):
        #game frame
        self.canvas = tk.Canvas(self.root, width=self.gameplay.width * self.TILE_SIZE, 
                                height=self.gameplay.height * self.TILE_SIZE, highlightthickness=0)
        self.canvas.place(x=350, y=90)
        self.canvas.bind("<Button-1>", lambda event: self.canvas_click(event))

        #title and step label
        self.title = tk.Label(self.root, text="Sokoban", font=("Arial", 30, "bold"), bg="lightskyblue1")
        self.title.place(x=560, y=20)
        self.stepLabel = tk.Label(self.root, text=f"Step: 0", font=("Arial", 20), bg="lightskyblue1")
        self.stepLabel.place(x=980, y=100)
        self.visitedLabel = tk.Label(self.root, text=f"Visited: 0", font=("Arial", 20), bg="lightskyblue1")
        self.visitedLabel.place(x=980, y=150)

        #button frame
        self.btnFrame = tk.Frame(self.root, width=200, height=500, background="navajo white")
        self.btnFrame.place(x=100, y=120)
        self.btnFrame.pack_propagate(0) # don't shrink
        BUTTON_WIDTH = 10
        PADDING = 15
        self.btnUndo = tk.Button(self.btnFrame, text="Undo", font=("Arial", 20), width=10, command=self.undo)
        self.btnUndo.pack(pady=PADDING)
        #combobox for algorithm
        cbAlgo = ttk.Combobox(self.btnFrame, values=["BFS", "DFS", "IDS", "UCS", "Greedy","A*","Beam"], font=("Arial", 20), 
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

        # choose element for level editor
        # use square button with element image as background
        # and bind click event to change element
        self.btnFrame2 = tk.Frame(self.root, width=200, height=200, background="lightskyblue1")
        self.btnFrame2.place(x=980, y=200)
        self.btnFrame2.grid_propagate(0)
        self.btnWall = tk.Button(self.btnFrame2, image=self.wall_image,
                                    command=lambda: self.change_element(self.gameplay.WALL_SYMBOL))
        self.btnWall.grid(row=0, column=0, padx=5, pady=5)
        self.btnEmpty = tk.Button(self.btnFrame2, image=self.empty_image,
                                    command=lambda: self.change_element(self.gameplay.EMPTY_SYMBOL))
        self.btnEmpty.grid(row=0, column=1, padx=5, pady=5)
        self.btnTarget = tk.Button(self.btnFrame2, image=self.target_image,
                                    command=lambda: self.change_element(self.gameplay.TARGET_SYMBOL))
        self.btnTarget.grid(row=1, column=0, padx=5, pady=5)
        self.btnBox = tk.Button(self.btnFrame2, image=self.box_image,
                                    command=lambda: self.change_element(self.gameplay.BOX_SYMBOL))
        self.btnBox.grid(row=1, column=1, padx=5, pady=5)
        self.btnPlayer = tk.Button(self.btnFrame2, image=self.player_image,
                                    command=lambda: self.change_element(self.gameplay.PLAYER_SYMBOL))
        self.btnPlayer.grid(row=0, column=3, padx=5, pady=5)
        self.selectedElement = self.gameplay.WALL_SYMBOL # default element
        self.selectedElementLabel = tk.Label(self.btnFrame2, text="Selected:", font=("Arial", 20), bg="lightskyblue1")
        self.selectedElementLabel.grid(row=2, column=0, columnspan=2, pady=5)
        # selected element image label
        self.selectedImage = tk.Label(self.btnFrame2, image=self.wall_image)
        self.selectedImage.grid(row=2, column=2, columnspan=2, pady=5)
    def change_element(self, element):
        self.selectedElement = element
        # change selected element image label
        if element == self.gameplay.WALL_SYMBOL:
            self.selectedImage.config(image=self.wall_image)
        elif element == self.gameplay.EMPTY_SYMBOL:
            self.selectedImage.config(image=self.empty_image)
        elif element == self.gameplay.TARGET_SYMBOL:
            self.selectedImage.config(image=self.target_image)
        elif element == self.gameplay.BOX_SYMBOL:
            self.selectedImage.config(image=self.box_image)
        elif element == self.gameplay.PLAYER_SYMBOL:
            self.selectedImage.config(image=self.player_image)
    def canvas_click(self, event):
        # print row and column number
        row = event.y // self.TILE_SIZE
        col = event.x // self.TILE_SIZE
        if self.selectedElement == self.gameplay.PLAYER_SYMBOL:
            # move player to new position
            cur_row, cur_col = np.argwhere(self.gameplay.board == self.gameplay.PLAYER_SYMBOL)[0]
            self.gameplay.board[cur_row][cur_col] = self.gameplay.EMPTY_SYMBOL
        elif self.selectedElement == self.gameplay.TARGET_SYMBOL or \
            self.gameplay.board[row][col] == self.gameplay.TARGET_SYMBOL:
            self.gameplay.board[row][col] = self.selectedElement
            # reload targets
            self.gameplay.targets = np.argwhere(self.gameplay.board == self.gameplay.TARGET_SYMBOL).tolist()

        self.gameplay.board[row][col] = self.selectedElement
        self.draw_board(self.gameplay.board)   
    def undo(self):
        if self.gameplay.undo():
            self.stepLabel.config(text=f"Step: {self.gameplay.step}")
            self.draw_board(self.gameplay.board)
    def load_level(self, level):
        self.gameplay.load_level(level)
        self.stepLabel.config(text=f"Step: 0")
        self.draw_board(self.gameplay.board)
    def solve(self, choice):
        if choice == "BFS":
            result = self.solveBFS()
        elif choice == "DFS":
            result = self.solveDFS()
        elif choice == "IDS":
            result = self.solveIDS()
        elif choice == "UCS":
            result = self.solveUCS()
        elif choice == "Greedy":
            result = self.solveGreedy()
        elif choice == "A*":
            result = self.solveAStar()
        elif choice == "Beam":
            result = self.solveBeam(k=2)
        if not result:
            messagebox.showinfo("No solution", "No solution found!")
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
    def solveUCS(self):
        visited = set()
        queue = deque([(self.gameplay, [], 0)])
        visited.add(tuple(self.gameplay.board.flatten()))

        while queue:
            current_gameplay, path, cost = queue.popleft()

            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True

            for new_gameplay, move in self.getChildren(current_gameplay):
                if tuple(new_gameplay.board.flatten()) not in visited:
                    visited.add(tuple(new_gameplay.board.flatten()))
                    queue.append((new_gameplay, path + [move], new_gameplay.step))
                    queue = deque(sorted(queue, key=lambda x: x[2]))
        return False
    def solveDFS(self):
        visited = set()
        stack = deque([(self.gameplay, [])])
        visited.add(tuple(self.gameplay.board.flatten()))

        while stack:
            current_gameplay, path = stack.pop()

            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True

            for new_gameplay, move in self.getChildren(current_gameplay):
                if tuple(new_gameplay.board.flatten()) not in visited:
                    visited.add(tuple(new_gameplay.board.flatten()))
                    stack.append((new_gameplay, path + [move]))
        return False
    def solveIDS(self):
        max_depth = 5
        visited = set()
        latestStates = deque([(self.gameplay, [], max_depth)])
        visited.add(tuple(self.gameplay.board.flatten()))
        while latestStates:
            stack = latestStates.copy()
            latestStates.clear()
            max_depth += 5
            while stack:
                current_gameplay, path, depth = stack.pop()
                
                #check win state
                if current_gameplay.check_win():
                    self.visitedLabel["text"] = f"Visited: {len(visited)}"
                    self.animateSolution(path)
                    return True
                
                if depth == 0:
                    latestStates.append((current_gameplay, path, max_depth))
                    continue
                for new_gameplay, move in self.getChildren(current_gameplay):
                    if tuple(new_gameplay.board.flatten()) not in visited:
                        visited.add(tuple(new_gameplay.board.flatten()))
                        stack.append((new_gameplay, path + [move], depth - 1))
        return False
    def solveGreedy(self):
        visited = set()
        queue = deque([(self.gameplay, [],0)])
        visited.add(tuple(self.gameplay.board.flatten()))

        while queue:
            current_gameplay, path, cost = queue.popleft()

            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True

            for new_gameplay, move in self.getChildren(current_gameplay):
                if tuple(new_gameplay.board.flatten()) not in visited:
                    visited.add(tuple(new_gameplay.board.flatten()))
                    queue.append((new_gameplay, path + [move], self.heuristic(new_gameplay)))
                    queue = deque(sorted(queue, key=lambda x: x[2]))
        return False
    def solveAStar(self):
        visited = set()
        queue = deque([(self.gameplay, [],0)])
        visited.add(tuple(self.gameplay.board.flatten()))

        while queue:
            current_gameplay, path, cost = queue.popleft()

            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True

            for new_gameplay, move in self.getChildren(current_gameplay):
                if tuple(new_gameplay.board.flatten()) not in visited:
                    visited.add(tuple(new_gameplay.board.flatten()))
                    queue.append((new_gameplay, path + [move], self.heuristic(new_gameplay) + new_gameplay.step))
                    queue = deque(sorted(queue, key=lambda x: x[2]))
        return False
    def heuristic(self, gameplay):
        #distance from box to the nearest target
        box_positions = np.argwhere(gameplay.board == gameplay.BOX_SYMBOL).tolist()
        #exclude box that is already on target
        box_positions = [box for box in box_positions if box not in gameplay.targets]
        # target_positions = np.argwhere(gameplay.board == gameplay.TARGET_SYMBOL).tolist()
        target_positions = gameplay.targets
        total_distance = 0
        for box_position in box_positions:
            min_distance = 100000
            for target_position in target_positions:
                distance = abs(box_position[0] - target_position[0]) + abs(box_position[1] - target_position[1])
                if distance < min_distance:
                    min_distance = distance
            total_distance += min_distance
            
        return total_distance
    def solveBeam(self, k=3):
        visited = set()
        queue = deque([(self.gameplay, [])])
        visited.add(tuple(self.gameplay.board.flatten()))
        while queue:
            k_loop = k
            current_gameplay, path = queue.popleft()
    
            if current_gameplay.check_win():
                self.visitedLabel["text"] = f"Visited: {len(visited)}"
                self.animateSolution(path)
                return True
            
            schedule = self.getChildren(current_gameplay)
            schedule = sorted(schedule , key=lambda x: self.heuristic(x[0]))
            # Sinh các trạng thái kế tiếp và thêm vào queue
            for new_gameplay, move in schedule:
                if tuple(new_gameplay.board.flatten()) not in visited:
                    if k_loop > 0:
                        visited.add(tuple(new_gameplay.board.flatten()))
                        queue.append((new_gameplay, path + [move]))
                        k_loop = k_loop - 1
                    else:
                        break

        return False
    def animateSolution(self, path):
        for move in path:
            self.gameplay.move_player(move)
            self.stepLabel.config(text=f"Step: {self.gameplay.step}")
            self.draw_board(self.gameplay.board)
            self.root.update()
            time.sleep(0.1)
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

        empty_image = Image.open("images/floor.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.empty_image = ImageTk.PhotoImage(empty_image)

        box_target_image = Image.open("images/box_on_target.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.box_target_image = ImageTk.PhotoImage(box_target_image)

        target_image = Image.open("images/target.png").resize((self.TILE_SIZE, self.TILE_SIZE))
        self.target_image = ImageTk.PhotoImage(target_image)

    def move_player(self, event):
        directions = ["Up", "Down", "Left", "Right", "w", "s", "a", "d"]
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
                        self.canvas.create_image(x+25, y+25, image=self.box_target_image)
                    else:
                        self.canvas.create_image(x+25, y+25, image=self.box_image)
                elif cell == self.gameplay.TARGET_SYMBOL:
                    self.canvas.create_image(x+25,y+25, image=self.empty_image)
                    # self.canvas.create_oval(x+20, y+20, x+30, y+30, fill='red')
                    self.canvas.create_image(x+25,y+25, image=self.target_image)
                elif cell == self.gameplay.PLAYER_SYMBOL:
                    self.canvas.create_image(x+25,y+25, image=self.empty_image)
                    self.canvas.create_image(x+25, y+25, image=self.player_image)

if __name__ == "__main__":
    root = tk.Tk()
    game = Sokoban(root)
    root.mainloop()