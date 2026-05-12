import tkinter as tk

import numpy as np

import ai

# Kolory elementów gry.
BG = "#000000"
TEXT = "#FFFFFF"  
SNAKE_HEAD = "#FFFF00"
SNAKE_BODY = "#00DD00"
FOOD = "#FF0000"


class SnakeGame:
    # Macierz planszy, 0 puste, 1 wąż, 2 jedzenie.
    grid: list[list[int]]

    @staticmethod
    def add(a: tuple[int, int], b: tuple[int, int]):
        #(x, y) + (dx, dy) — wektor kierunku to np. (1,0) w prawo.
        return (a[0] + b[0], a[1] + b[1])

    @staticmethod
    def opposite(a: tuple[int, int], b: tuple[int, int]) -> bool:
        #sprawdza czy kierunek nie jest przeciwny do kierunku węża
        return a[0] == -b[0] and a[1] == -b[1]

    def _can_enter_cell(self, x: int, y: int) -> bool:
        #Czy komórka (x, y) jest na planszy i jest pusta albo z jedzeniem.
        if x < 0 or x >= self.grid_w or y < 0 or y >= self.grid_h:
            return False
        return self.grid[y][x] in (0, 2)

    # znalezienie miejsca na jedzonko
    @staticmethod
    def place_food(grid: list[list[int]]) -> tuple[int, int] | None:
        #Losowa pusta komórka; None gdy plansza pełna (wygrana / brak miejsca).
        grid_h = len(grid)
        grid_w = len(grid[0])

        # lista pustych komórek
        empty_cells: list[tuple[int, int]] = []
        for y in range(grid_h):
            #row = grid[y]
            for x in range(grid_w):
                if grid[y][x] == 0:
                    empty_cells.append((x, y))
        if not empty_cells:
            return None
        return empty_cells[np.random.randint(len(empty_cells))]

    # rysowanie kwadratu, cell to szerokość komórki w pikselach
    @staticmethod
    def cell_rect(cell: int, x: int, y: int) -> tuple[int, int, int, int]:
        x0 = x * cell 
        y0 = y * cell 
        x1 = (x + 1) * cell 
        y1 = (y + 1) * cell 
        return x0, y0, x1, y1

    def __init__(
        self,
        grid_w: int,
        grid_h: int,
        snake_len: int,
        delay_ms: int,
        cell_px: int,
        bfs_retry_every_moves: int,
        logs: int = 0,
    ):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.snake_len = max(2, min(int(snake_len), grid_w, grid_w // 2))
        self.logs = max(0, int(logs))
        self.logging_mode = self.logs > 0
        # gdy tryb logowania, minimalny delay
        if self.logging_mode:
            self.delay_ms = 1
        else:
            self.delay_ms = max(1, int(delay_ms))
        self.cell = max(1, int(cell_px))
        self.bfs_retry_every_moves = max(0, int(bfs_retry_every_moves))

        # tworzenie planszy z samymi zerami
        self.grid = [[0] * self.grid_w for _ in range(self.grid_h)] 

        #okno rozmiar
        self.width = self.grid_w * self.cell 
        self.height = self.grid_h * self.cell

        #ustawienia Okna
        self.tk = tk.Tk()
        self.tk.title("Snake")
        self.tk.configure(bg=BG)
        self.tk.resizable(False, False)
        self.canvas = tk.Canvas(self.tk, width=self.width, height=self.height, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.tk.bind("<KeyPress>", self.on_key)
        if self.logging_mode:
            self.tk.withdraw()

        self._after_id: str | None = None  
        self.ai_dirs: list[tuple[int, int]] = []  # kierunki z BFS
        self.bfs_nodes_last = 0  # liczba ostatnio sprawdzonych nodów, do wyświetlenia
        self.bfs_path_missing = False  # Czy znalazł ścieżkę do jedzenia
        self.bfs_retry_counter = 0  # Ruchy od ostatniego planu BFS, gdy brak ścieżki (do retry)
        self.reset()


    def generate_path(self):
        # generowanie listy kierunków przy pomocy BFS i zwróć ile nodów sprawdził BFS
        self.ai_dirs, self.bfs_nodes_last = ai.generate_directions(self.grid, self.snake[0], self.food)
        # sprawdzenie czy BFS nie zwrócił ścieżki do jedzenia
        self.bfs_path_missing = ai.bfs_no_path_to_food(self.ai_dirs, self.food, self.snake[0])
        self.bfs_retry_counter = 0

    def reset(self):
        # zerowanie planszy
        w, h = self.grid_w, self.grid_h
        for y in range(h):
            for x in range(w):
                self.grid[y][x] = 0

        # Start w poziomie od środka w lewo: głowa na (sx,sy), reszta ciała na zachód.
        sx, sy = w // 2, h // 2
        # Długość startowa: nie większa niż szerokość ani niż połowa szerokości; co najmniej 2 segmenty.
        length = max(2, min(self.snake_len, w, w // 2))
        self.snake = [(sx - i, sy) for i in range(length)]
        self.dir = (1, 0) # kierunek węża w prawo
        self.pending = self.dir # kierunek węża w następnym kroku
        

        for x, y in self.snake: # ustawienie cellsów węża na 1
            self.grid[y][x] = 1

        self.ai_dirs = [] # kolejka kierunków z BFS

        self.food = self.place_food(self.grid)
        if self.food is not None:
            fx, fy = self.food
            self.grid[fy][fx] = 2
        self.generate_path()

        self.score = 0
        self.snake_length = len(self.snake)
        self.game_over = False
        self.game_won = False


    # anykey na reset
    def on_key(self, _e: tk.Event):
        if self.game_over:
            self.reset()

    def next_ai_dir(self) -> tuple[int, int]:
        # jak BFS nie znajdzie drogi (pusta kolejka kroków)
        if not self.ai_dirs:
            # leci po podanych kierunkach
            for cand in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                # sprawdza czy kierunek nie jest przeciwny do kierunku węża
                if self.opposite(cand, self.dir):
                    continue
                nx, ny = self.add(self.snake[0], cand)
                # granice planszy oraz pole puste (0) albo jedzenie (2)
                if self._can_enter_cell(nx, ny):
                    return cand
            # Wszystkie kierunki złe — zostaje bieżący (często kończy grę w następnym kroku)
            return self.dir
        return self.ai_dirs.pop(0)

    def step(self):
        if self.game_over:
            return

        # Kierunek węża
        self.dir = self.next_ai_dir()

        # nowa pozycja głowy, dodanie aktualnej pozycji i wektora kierunku
        nx, ny = self.add(self.snake[0] , self.dir)

        # kolizja z planszą
        if (nx < 0 or nx >= self.grid_w) or (ny < 0 or ny >= self.grid_h):
            self.game_over = True
            return

        new_head = (nx, ny)

        cell = self.grid[ny][nx] # co jest w miejscu nowej głowy
        will_grow = cell == 2 # czy w miejscu nowej głowy wciąż jest jedzenie
        tail = self.snake[-1] # ostatnie pole ciała

        # Kolizja z ciałem gdy nowa głowa najedzie na rosnący ogon
        if cell == 1 and not (new_head == tail and not will_grow):
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        self.grid[ny][nx] = 1

        # głowa najechała na jedzenie
        if will_grow: 
            self.score += 1
            food = self.place_food(self.grid)
            self.food = food
            if food is not None:
                fx, fy = food
                self.grid[fy][fx] = 2
            cells_total = self.grid_w * self.grid_h
            if len(self.snake) == cells_total:
                self.game_over = True
                self.game_won = True
            else:
                self.generate_path()
        else:
            tx, ty = self.snake.pop()
            self.grid[ty][tx] = 0  # Ogon przesunął się — stara komórka znowu pusta

        self.snake_length = len(self.snake)

        # jeśli BFS nie znajdzie drogi do jedzenia, wykonuje ponownie BFS co bfs_retry_every_moves kroków
        if not self.game_over and self.bfs_retry_every_moves > 0 and self.bfs_path_missing:
            self.bfs_retry_counter += 1
            if self.bfs_retry_counter >= self.bfs_retry_every_moves:
                self.generate_path()

    def draw(self) -> None:
        # w tybie logowania wyników nie wyświta planszy
        if self.logging_mode:
            return
        self.canvas.delete("all")

        head = self.snake[0]
        for y in range(self.grid_h):
            row = self.grid[y]
            for x in range(self.grid_w):
                v = row[x]
                if v == 2:
                    self.canvas.create_rectangle(*self.cell_rect(self.cell, x, y), fill=FOOD, outline="")
                elif v == 1:
                    color = SNAKE_HEAD if (x, y) == head else SNAKE_BODY
                    self.canvas.create_rectangle(*self.cell_rect(self.cell, x, y), fill=color, outline="")


        self.canvas.create_text(
            5,
            5,
            text="Punkty: "+self.score.__str__()+"\n"+
            "Wąż: "+self.snake_length.__str__()+"\n"+
            "BFS, ilość nodów: "+self.bfs_nodes_last.__str__(),
            fill=TEXT,
            font=("Comic Sans MS", 11, "bold"),
            anchor="nw",
        )
        if self.bfs_path_missing:
            self.canvas.create_text(
                5,
                64,
                text="BFS: nie znaleziono ścieżki do jedzenia",
                fill=TEXT,
                font=("Comic Sans MS", 10, "bold"),
                anchor="nw",
            )

        if self.game_over:
            title = "Wygrana" if self.game_won else "Koniec gry"
            self.canvas.create_text(
                self.width // 2, self.height // 2 - 16, text=title, fill=TEXT, font=("Comic Sans MS", 14, "bold")
            )
            self.canvas.create_text(
                self.width // 2,
                self.height // 2 + 16,
                text="Naciśnij dowolny klawisz, aby zagrać ponownie",
                fill=TEXT,
                font=("Comic Sans MS", 10),
            )

    # główna pętla gry (tylko tryb z oknem)
    def loop(self):
        self.step()
        self.draw()
        self._after_id = self.tk.after(self.delay_ms, self.loop)

    def _run_logs_simulation(self):
        # symulacja rund, max_steps ogranicza liczbę kroków w teście
        max_steps = max(5000, self.grid_w * self.grid_h * 500)
        lines = []
        for game_round in range(1, self.logs + 1):
            self.reset()
            kroki = 0
            while not self.game_over and kroki < max_steps:
                self.step()
                kroki += 1
            if self.game_over:
                lines.append(
                    f"runda={game_round}; punkty={self.score}; dlugosc_weza={len(self.snake)}\n"
                )
        if lines:
            with open("logs.txt", "a", encoding="utf-8") as plik:
                plik.writelines(lines)

    def run_game(self):
        if self.logging_mode:
            self._run_logs_simulation()
            self.tk.destroy()
            return
        self.loop()
        self.tk.mainloop()


