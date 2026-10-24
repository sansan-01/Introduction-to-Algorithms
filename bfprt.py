
import random
import re
import tkinter as tk
from tkinter import messagebox

# ==========================================
# BFPRT / Median of Medians Visualization
# ==========================================

SAMPLE = [
    19, 1, 13, 5, 7,
    22, 2, 14, 8, 9,
    16, 3, 20, 10, 11,
    18, 4, 23, 15, 21,
    6, 12, 17
]

BG = "#F3F6FB"
BLUE = "#2563EB"
GREEN = "#15803D"
ORANGE = "#B45309"
RED = "#DC2626"


def bfprt(values, k, events, depth=0, purpose="查找目标"):
    """
    BFPRT：寻找第 k 小的元素
    k 从 1 开始。
    events 用来保存算法的可视化步骤。
    """
    n = len(values)

    events.append({
        "phase": "enter",
        "nums": values[:],
        "k": k,
        "depth": depth,
        "purpose": purpose
    })

    # 递归基例：最多 5 个元素，直接排序
    if n <= 5:
        ordered = sorted(values)
        result = ordered[k - 1]

        events.append({
            "phase": "base",
            "nums": values[:],
            "groups": [ordered],
            "k": k,
            "depth": depth,
            "purpose": purpose,
            "result": result
        })
        return result

    # Step 1: 每 5 个元素分成一组
    groups = [
        sorted(values[i:i + 5])
        for i in range(0, n, 5)
    ]

    # Step 2: 取每组的中位数
    # 不足 5 个时，取靠左的中间元素
    medians = [
        group[(len(group) - 1) // 2]
        for group in groups
    ]

    events.append({
        "phase": "groups",
        "nums": values[:],
        "groups": groups,
        "medians": medians,
        "k": k,
        "depth": depth,
        "purpose": purpose
    })

    # Step 3: 递归求中位数的中位数
    pivot = bfprt(
        medians,
        (len(medians) + 1) // 2,
        events,
        depth + 1,
        "选择 Pivot"
    )

    # Step 4: 根据 Pivot 进行三路划分
    left = [x for x in values if x < pivot]
    equal = [x for x in values if x == pivot]
    right = [x for x in values if x > pivot]

    base_event = {
        "nums": values[:],
        "groups": groups,
        "medians": medians,
        "pivot": pivot,
        "left": left,
        "equal": equal,
        "right": right,
        "k": k,
        "depth": depth,
        "purpose": purpose
    }

    events.append({
        **base_event,
        "phase": "partition"
    })

    # Step 5: 只递归包含目标排名的部分
    if k <= len(left):
        events.append({
            **base_event,
            "phase": "choose",
            "side": "LEFT",
            "new_k": k
        })
        return bfprt(
            left, k, events, depth + 1, purpose
        )

    if k <= len(left) + len(equal):
        events.append({
            **base_event,
            "phase": "answer",
            "result": pivot
        })
        return pivot

    new_k = k - len(left) - len(equal)

    events.append({
        **base_event,
        "phase": "choose",
        "side": "RIGHT",
        "new_k": new_k
    })

    return bfprt(
        right, new_k, events, depth + 1, purpose
    )


class BFPRTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("BFPRT Visualization")
        self.root.geometry("1000x750")
        self.root.configure(bg=BG)

        self.events = []
        self.index = 0
        self.playing = False
        self.job = None

        self.speed = tk.IntVar(value=450)
        self.k_var = tk.StringVar(value="12")

        self.create_ui()
        self.set_sample(SAMPLE)

    def create_ui(self):
        # 标题
        tk.Label(
            self.root,
            text="BFPRT — Median of Medians",
            font=("Arial", 23, "bold"),
            bg=BG,
            fg="#0F172A"
        ).pack(anchor="w", padx=20, pady=(15, 2))

        tk.Label(
            self.root,
            text="Deterministic Linear-Time Selection",
            font=("Arial", 11),
            bg=BG,
            fg="#64748B"
        ).pack(anchor="w", padx=20)

        # 输入区域
        inputs = tk.Frame(self.root, bg=BG)
        inputs.pack(fill="x", padx=20, pady=12)

        self.data_entry = tk.Entry(
            inputs, font=("Arial", 11)
        )
        self.data_entry.pack(
            side="left", fill="x", expand=True
        )

        tk.Label(
            inputs, text="  k = ", bg=BG
        ).pack(side="left")

        tk.Entry(
            inputs, textvariable=self.k_var,
            width=5, font=("Arial", 11)
        ).pack(side="left")

        tk.Button(
            inputs, text="Load",
            command=self.load_input
        ).pack(side="left", padx=7)

        tk.Button(
            inputs, text="Random",
            command=self.random_data
        ).pack(side="left")

        # 主要显示区域
        main = tk.Frame(self.root, bg=BG)
        main.pack(
            fill="both", expand=True,
            padx=20, pady=5
        )

        left_frame = tk.Frame(main, bg="white")
        left_frame.pack(
            side="left", fill="both", expand=True,
            padx=(0, 12)
        )

        self.canvas = tk.Canvas(
            left_frame,
            width=540,
            height=510,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(
            fill="both", expand=True
        )

        right_frame = tk.Frame(
            main, bg="white", width=330
        )
        right_frame.pack(
            side="right", fill="both"
        )
        right_frame.pack_propagate(False)

        tk.Label(
            right_frame,
            text="Operation History",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(anchor="w", padx=12, pady=12)

        self.stats = tk.Label(
            right_frame,
            text="",
            font=("Arial", 10),
            bg="white",
            fg="#64748B"
        )
        self.stats.pack(anchor="w", padx=12)

        log_frame = tk.Frame(
            right_frame, bg="white"
        )
        log_frame.pack(
            fill="both", expand=True,
            padx=12, pady=10
        )

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log = tk.Text(
            log_frame,
            font=("Menlo", 10),
            bg="#F8FAFC",
            relief="flat",
            wrap="word",
            yscrollcommand=scrollbar.set,
            state="disabled"
        )
        self.log.pack(
            side="left", fill="both", expand=True
        )
        scrollbar.config(command=self.log.yview)

        for tag, color in [
            ("groups", BLUE),
            ("base", GREEN),
            ("partition", ORANGE),
            ("choose", BLUE),
            ("answer", GREEN),
            ("finish", GREEN)
        ]:
            self.log.tag_configure(
                tag, foreground=color
            )

        # 控制区域
        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", padx=20, pady=10)

        for name, command in [
            ("Start", self.start),
            ("Pause", self.pause),
            ("Step", self.single_step),
            ("Reset", self.reset)
        ]:
            tk.Button(
                controls,
                text=name,
                command=command,
                width=11,
                font=("Arial", 11),
                bg="#E2E8F0",
                relief="flat",
                pady=6
            ).pack(side="left", padx=(0, 10))

        tk.Label(
            controls,
            text="Delay (ms)",
            bg=BG
        ).pack(side="left", padx=(20, 3))

        tk.Scale(
            controls,
            from_=50,
            to=1500,
            orient="horizontal",
            variable=self.speed,
            length=210,
            bg=BG,
            highlightthickness=0
        ).pack(side="left")

        self.status = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 11),
            bg=BG,
            fg="#334155"
        )
        self.status.pack(
            anchor="w", padx=20, pady=(0, 12)
        )

    def set_sample(self, values):
        self.data_entry.delete(0, "end")
        self.data_entry.insert(
            0, ", ".join(map(str, values))
        )
        self.k_var.set(str((len(values) + 1) // 2))
        self.load_input()

    def random_data(self):
        values = random.sample(range(1, 100), 23)
        self.set_sample(values)

    def load_input(self):
        try:
            parts = re.split(
                r"[,，\s]+",
                self.data_entry.get().strip()
            )
            values = [int(x) for x in parts if x]

            if not 1 <= len(values) <= 60:
                raise ValueError(
                    "Please enter 1 to 60 integers."
                )

            k = int(self.k_var.get())

            if not 1 <= k <= len(values):
                raise ValueError(
                    "k must be between 1 and n."
                )

        except ValueError as error:
            messagebox.showerror(
                "Invalid Input", str(error)
            )
            return

        self.pause()

        self.values = values[:]
        self.k = k
        self.events = []

        result = bfprt(
            values, k, self.events
        )

        self.events.append({
            "phase": "finish",
            "nums": values[:],
            "k": k,
            "depth": 0,
            "result": result,
            "purpose": "最终结果"
        })

        self.index = 0
        self.clear_log()
        self.draw(None)
        self.update_stats()
        self.status.config(
            text=f"Ready — Find the {k}-th smallest value"
        )

    def clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def add_log(self, message, tag="normal"):
        self.log.config(state="normal")
        self.log.insert(
            "end",
            f"{self.index:03d}  {message}\n",
            tag
        )
        self.log.see("end")
        self.log.config(state="disabled")

    def update_stats(self):
        self.stats.config(
            text=(
                f"Input size: {len(self.values)}\n"
                f"Target rank: {self.k}\n"
                f"Step: {self.index}/{len(self.events)}"
            )
        )

    def tile(self, x, y, value, color):
        self.canvas.create_rectangle(
            x, y, x + 56, y + 31,
            fill=color,
            outline="#CBD5E1"
        )
        self.canvas.create_text(
            x + 28, y + 16,
            text=str(value),
            font=("Arial", 12, "bold"),
            fill="#0F172A"
        )

    def draw(self, event):
        self.canvas.delete("all")

        if event is None:
            event = {
                "phase": "enter",
                "nums": self.values,
                "k": self.k,
                "depth": 0,
                "purpose": "初始数组"
            }

        phase = event["phase"]
        nums = event["nums"]
        depth = event.get("depth", 0)

        self.canvas.create_text(
            20, 23,
            anchor="w",
            text=f"Level {depth}  |  {event['purpose']}",
            font=("Arial", 15, "bold"),
            fill="#0F172A"
        )

        self.canvas.create_text(
            20, 51,
            anchor="w",
            text=(
                f"n = {len(nums)}, "
                f"k = {event['k']}  "
                "(1-based rank)"
            ),
            font=("Arial", 11),
            fill="#64748B"
        )

        # 将当前元素按每行最多 5 个展示
        groups = event.get("groups")

        if groups is None:
            groups = [
                nums[i:i + 5]
                for i in range(0, len(nums), 5)
            ]

        self.canvas.create_text(
            20, 88,
            anchor="w",
            text=(
                "Groups of 5"
                if phase != "enter"
                else "Original groups"
            ),
            font=("Arial", 12, "bold")
        )

        max_rows = 6

        for i, group in enumerate(groups[:max_rows]):
            y = 112 + i * 43

            self.canvas.create_text(
                20, y + 16,
                anchor="w",
                text=f"Group {i + 1}",
                font=("Arial", 10),
                fill="#64748B"
            )

            for j, value in enumerate(group):
                color = "#E8EFFB"

                if phase != "enter":
                    median_index = (
                        len(group) - 1
                    ) // 2

                    if phase == "base":
                        median_index = event["k"] - 1

                    if j == median_index:
                        color = "#BBF7D0"

                self.tile(
                    125 + j * 70,
                    y, value, color
                )

        y = 112 + min(len(groups), max_rows) * 43

        if len(groups) > max_rows:
            self.canvas.create_text(
                20, y,
                anchor="w",
                text=(
                    f"... {len(groups) - max_rows} "
                    "more groups"
                ),
                fill="#64748B"
            )
            y += 20

        medians = event.get("medians", [])

        if medians:
            self.canvas.create_text(
                20, y + 12,
                anchor="w",
                text=(
                    "Group medians: "
                    + ", ".join(map(str, medians))
                ),
                fill=BLUE,
                font=("Arial", 11, "bold")
            )
            y += 29

        if "pivot" in event:
            self.canvas.create_text(
                20, y + 10,
                anchor="w",
                text=f"Pivot = {event['pivot']}",
                fill=GREEN,
                font=("Arial", 13, "bold")
            )
            y += 32

        if phase in ("partition", "choose", "answer"):
            data = [
                ("LEFT", event["left"], "#DBEAFE"),
                ("EQUAL", event["equal"], "#BBF7D0"),
                ("RIGHT", event["right"], "#FEE2E2")
            ]

            for i, (name, values, color) in enumerate(data):
                x = 20 + i * 170

                self.canvas.create_rectangle(
                    x, y, x + 158, y + 42,
                    fill=color,
                    outline="#CBD5E1"
                )

                self.canvas.create_text(
                    x + 79, y + 12,
                    text=f"{name}: {len(values)}",
                    font=("Arial", 10, "bold")
                )

                preview = ", ".join(
                    map(str, values[:6])
                )

                if len(values) > 6:
                    preview += "..."

                self.canvas.create_text(
                    x + 79, y + 29,
                    text=preview,
                    font=("Arial", 9)
                )

        if "result" in event:
            self.canvas.create_text(
                20, min(y + 48, 495),
                anchor="w",
                text=f"Result = {event['result']}",
                fill=GREEN,
                font=("Arial", 15, "bold")
            )

    def describe(self, event):
        phase = event["phase"]

        if phase == "enter":
            return (
                f"Enter level {event['depth']}: "
                f"n={len(event['nums'])}, k={event['k']}"
            )

        if phase == "groups":
            return (
                "Sort groups, medians = "
                + str(event["medians"])
            )

        if phase == "base":
            return (
                f"Base case: rank {event['k']} "
                f"= {event['result']}"
            )

        if phase == "partition":
            return (
                f"Pivot {event['pivot']}: "
                f"L={len(event['left'])}, "
                f"E={len(event['equal'])}, "
                f"R={len(event['right'])}"
            )

        if phase == "choose":
            return (
                f"Choose {event['side']}, "
                f"new k={event['new_k']}"
            )

        if phase == "answer":
            return (
                f"Found rank {event['k']}: "
                f"{event['result']}"
            )

        return (
            f"FINISHED! Answer = {event['result']}"
        )

    def next_step(self):
        if self.index >= len(self.events):
            self.playing = False
            return False

        event = self.events[self.index]
        self.index += 1

        self.draw(event)

        message = self.describe(event)
        self.add_log(message, event["phase"])

        self.status.config(text=message)
        self.update_stats()

        if self.index >= len(self.events):
            self.playing = False

        return True

    def animate(self):
        self.job = None

        if not self.playing:
            return

        if self.next_step() and self.playing:
            self.job = self.root.after(
                self.speed.get(),
                self.animate
            )

    def start(self):
        if self.playing:
            return

        if self.index >= len(self.events):
            return

        self.playing = True
        self.animate()

    def pause(self):
        self.playing = False

        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def single_step(self):
        self.pause()
        self.next_step()

    def reset(self):
        self.pause()
        self.index = 0
        self.clear_log()
        self.draw(None)
        self.update_stats()
        self.status.config(text="Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = BFPRTVisualizer(root)
    root.mainloop()
