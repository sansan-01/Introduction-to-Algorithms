
import tkinter as tk
from tkinter import ttk

# ==========================================
# Sudoku Backtracking Visualization
# ==========================================

INITIAL_BOARD = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

COLORS = {
    "background": "#F3F6FB",
    "panel": "#FFFFFF",
    "original": "#E7EDF5",
    "empty": "#FFFFFF",
    "fill": "#BBF7D0",
    "backtrack": "#FECACA",
    "reject": "#FDE68A",
    "number": "#2563EB",
    "fixed_number": "#111827",
    "grid": "#CBD5E1",
    "border": "#334155",
    "green": "#15803D",
    "red": "#DC2626",
    "orange": "#B45309",
}


class SudokuVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Backtracking Visualizer")
        self.root.geometry("880x670")
        self.root.minsize(850, 640)
        self.root.configure(bg=COLORS["background"])

        self.board = []
        self.generator = None
        self.running = False
        self.completed = False
        self.job = None

        self.steps = 0
        self.attempts = 0
        self.fills = 0
        self.backtracks = 0

        self.delay = tk.IntVar(value=100)
        self.status_var = tk.StringVar(value="Ready")

        self.create_interface()
        self.reset()

    # --------------------------------------
    # Check Sudoku constraints
    # --------------------------------------
    def is_valid(self, row, col, num):
        for i in range(9):
            if self.board[row][i] == num:
                return False

            if self.board[i][col] == num:
                return False

        start_row = row // 3 * 3
        start_col = col // 3 * 3

        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.board[r][c] == num:
                    return False

        return True

    # --------------------------------------
    # Backtracking generator
    # --------------------------------------
    def solve(self):
        for row in range(9):
            for col in range(9):

                if self.board[row][col] != 0:
                    continue

                for num in range(1, 10):

                    # Show every candidate attempt
                    yield ("try", row, col, num)

                    if not self.is_valid(row, col, num):
                        yield ("reject", row, col, num)
                        continue

                    # Make a choice
                    self.board[row][col] = num
                    yield ("fill", row, col, num)

                    # Explore recursively
                    success = yield from self.solve()

                    if success:
                        return True

                    # Undo the choice
                    self.board[row][col] = 0
                    yield ("backtrack", row, col, num)

                return False

        return True

    # --------------------------------------
    # Create user interface
    # --------------------------------------
    def create_interface(self):
        header = tk.Frame(
            self.root, bg=COLORS["background"]
        )
        header.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            header,
            text="Sudoku Backtracking",
            font=("Arial", 23, "bold"),
            bg=COLORS["background"],
            fg="#0F172A"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Recursive search and backtracking visualization",
            font=("Arial", 11),
            bg=COLORS["background"],
            fg="#64748B"
        ).pack(anchor="w")

        main = tk.Frame(
            self.root, bg=COLORS["background"]
        )
        main.pack(fill="both", expand=True, padx=20)

        # Left panel
        left = tk.Frame(
            main, bg=COLORS["panel"]
        )
        left.pack(side="left", padx=(0, 15), anchor="n")

        self.canvas = tk.Canvas(
            left,
            width=450,
            height=450,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)

        # Right panel
        right = tk.Frame(
            main,
            bg=COLORS["panel"],
            width=340
        )
        right.pack(side="left", fill="both", expand=True)
        right.pack_propagate(False)

        tk.Label(
            right,
            text="Operation History",
            font=("Arial", 15, "bold"),
            bg="white",
            fg="#0F172A"
        ).pack(anchor="w", padx=12, pady=(12, 8))

        stats = tk.Frame(right, bg="white")
        stats.pack(fill="x", padx=12, pady=(0, 10))

        self.stats_label = tk.Label(
            stats,
            text="",
            font=("Arial", 11),
            bg="white",
            fg="#475569",
            justify="left"
        )
        self.stats_label.pack(anchor="w")

        log_frame = tk.Frame(right, bg="white")
        log_frame.pack(
            fill="both", expand=True,
            padx=12, pady=(0, 12)
        )

        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log = tk.Text(
            log_frame,
            width=35,
            height=20,
            font=("Menlo", 10),
            bg="#F8FAFC",
            fg="#334155",
            relief="flat",
            state="disabled",
            wrap="none",
            yscrollcommand=scrollbar.set
        )
        self.log.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.log.yview)

        self.log.tag_configure(
            "try", foreground="#475569"
        )
        self.log.tag_configure(
            "reject", foreground=COLORS["orange"]
        )
        self.log.tag_configure(
            "fill", foreground=COLORS["green"]
        )
        self.log.tag_configure(
            "backtrack", foreground=COLORS["red"]
        )
        self.log.tag_configure(
            "success", foreground=COLORS["green"]
        )

        # Bottom controls
        controls = tk.Frame(
            self.root, bg=COLORS["background"]
        )
        controls.pack(fill="x", padx=20, pady=(5, 15))

        buttons = tk.Frame(
            controls, bg=COLORS["background"]
        )
        buttons.pack(anchor="w")

        for title, command in [
            ("Start", self.start),
            ("Pause", self.pause),
            ("Step", self.single_step),
            ("Reset", self.reset),
        ]:
            tk.Button(
                buttons,
                text=title,
                command=command,
                width=10,
                font=("Arial", 11),
                bg="#E2E8F0",
                fg="#111827",
                relief="flat",
                padx=8,
                pady=6
            ).pack(side="left", padx=(0, 10))

        tk.Label(
            controls,
            text="Animation Delay (ms)",
            bg=COLORS["background"],
            fg="#475569",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(10, 0))

        tk.Scale(
            controls,
            from_=1,
            to=500,
            orient="horizontal",
            variable=self.delay,
            bg=COLORS["background"],
            highlightthickness=0,
            length=320
        ).pack(anchor="w")

        self.status_label = tk.Label(
            controls,
            textvariable=self.status_var,
            bg=COLORS["background"],
            fg="#334155",
            font=("Arial", 11)
        )
        self.status_label.pack(anchor="w")

    # --------------------------------------
    # Draw the Sudoku board
    # --------------------------------------
    def draw_board(self, active=None):
        self.canvas.delete("all")

        for row in range(9):
            for col in range(9):
                x = col * 50
                y = row * 50

                color = COLORS["empty"]

                if INITIAL_BOARD[row][col] != 0:
                    color = COLORS["original"]

                if active is not None:
                    action, r, c, num = active

                    if row == r and col == c:
                        if action == "fill":
                            color = COLORS["fill"]
                        elif action == "backtrack":
                            color = COLORS["backtrack"]
                        elif action == "reject":
                            color = COLORS["reject"]
                        elif action == "try":
                            color = "#DBEAFE"

                self.canvas.create_rectangle(
                    x, y, x + 50, y + 50,
                    fill=color,
                    outline=COLORS["grid"]
                )

                value = self.board[row][col]

                if value != 0:
                    fixed = INITIAL_BOARD[row][col] != 0

                    self.canvas.create_text(
                        x + 25,
                        y + 25,
                        text=str(value),
                        font=("Arial", 19, "bold"),
                        fill=(
                            COLORS["fixed_number"]
                            if fixed else COLORS["number"]
                        )
                    )

        # Thick 3x3 boundaries
        for i in range(0, 10, 3):
            p = i * 50

            self.canvas.create_line(
                p, 0, p, 450,
                fill=COLORS["border"],
                width=3
            )
            self.canvas.create_line(
                0, p, 450, p,
                fill=COLORS["border"],
                width=3
            )

    # --------------------------------------
    # Append operation history
    # --------------------------------------
    def add_log(self, message, tag="try"):
        self.log.config(state="normal")
        self.log.insert("end", message + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def update_stats(self):
        self.stats_label.config(
            text=(
                f"Events: {self.steps}    "
                f"Attempts: {self.attempts}\n"
                f"Fills: {self.fills}    "
                f"Backtracks: {self.backtracks}"
            )
        )

    # --------------------------------------
    # Execute one algorithm event
    # --------------------------------------
    def execute_step(self):
        if self.completed:
            return False

        if self.generator is None:
            self.generator = self.solve()

        try:
            action, row, col, num = next(self.generator)

            self.steps += 1

            position = f"R{row + 1}C{col + 1}"

            if action == "try":
                self.attempts += 1
                message = f"TRY       {position} = {num}"

            elif action == "reject":
                message = f"REJECT    {position} = {num}"

            elif action == "fill":
                self.fills += 1
                message = f"FILL      {position} = {num}"

            else:
                self.backtracks += 1
                message = f"BACKTRACK {position} = {num}"

            self.add_log(
                f"{self.steps:05d}  {message}",
                action
            )

            self.draw_board(
                (action, row, col, num)
            )
            self.update_stats()
            self.status_var.set(message)

            return True

        except StopIteration as result:
            self.completed = True
            self.running = False
            self.draw_board()

            if result.value:
                self.status_var.set("Sudoku solved!")
                self.add_log(
                    "===== SUDOKU SOLVED =====",
                    "success"
                )
            else:
                self.status_var.set("No solution found")
                self.add_log("No solution found")

            return False

    # --------------------------------------
    # Animation controls
    # --------------------------------------
    def animate(self):
        self.job = None

        if not self.running:
            return

        if self.execute_step():
            self.job = self.root.after(
                self.delay.get(),
                self.animate
            )

    def start(self):
        if self.running or self.completed:
            return

        self.running = True
        self.animate()

    def pause(self):
        self.running = False

        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

        if not self.completed:
            self.status_var.set("Paused")

    def single_step(self):
        self.pause()
        self.execute_step()

    def reset(self):
        self.pause()

        # Close old generator before replacing board
        if self.generator is not None:
            self.generator.close()

        self.board = [
            row[:] for row in INITIAL_BOARD
        ]

        self.generator = None
        self.completed = False
        self.steps = 0
        self.attempts = 0
        self.fills = 0
        self.backtracks = 0

        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        self.draw_board()
        self.update_stats()
        self.status_var.set("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuVisualizer(root)
    root.mainloop()
