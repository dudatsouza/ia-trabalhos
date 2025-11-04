# IMPORTS EXTERNAL
import os
import random
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import matplotlib.pyplot as plt

# ADJUST SYSTEM PATH TO INCLUDE THE SRC FOLDER FOR MODULE RESOLUTION
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# IMPORTS INTERNAL
# CORE
from core.eight_queens_representation import EightQueensProblem
# TOOLS
from tools.measure_time_memory import measure_time_memory
# LOCAL SEARCH
from local_search.random_restarts import hill_climbing_with_random_restarts
from local_search.sideways_moves import hill_climbing_with_sideways_moves
from local_search.simulated_annealing import simulated_annealing
# COMPARISON
from comparisons.compare_hill_climbing import compare_hill_climbing_algorithms
# VISUALIZATION
from visualization.queen_gif import generate_gif_from_states, diff_states

# CONSTANTS FOR RENDERING
BOARD_SIZE = 8
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"
HIGHLIGHT_FROM = "#f9e79f"
HIGHLIGHT_TO = "#82e0aa"
BEST_CANDIDATE_COLOR = "#f5b7b1"

class App(tk.Tk):
    def __init__(self) -> None:
        random.seed(42)
        super().__init__()
        self.title("Eight Queens - Hill Climbing Playground")
        self.geometry("1100x780")
        self.resizable(False, False)

        self.problem = EightQueensProblem()
        self.current_algorithm = "Initial board"
        self.current_states: List[List[int]] = []
        self.current_history: List[int] = []
        self.current_metadata: Dict[str, Any] = {}

        self._animating = False
        self._anim_after_id: Optional[str] = None
        self._animation_index = 0
        self._animation_states: List[List[int]] = []
        self._animation_history: List[int] = []

        self.sideways_limit_var = tk.IntVar(value=100)
        self.rr_allow_sideways_var = tk.BooleanVar(value=True)
        self.rr_max_moves_var = tk.IntVar(value=20)
        self.rr_max_restarts_var = tk.IntVar(value=100)
        self.annealing_temp_var = tk.DoubleVar(value=400.0)
        self.annealing_cooling_var = tk.StringVar(value="linear")
        self.annealing_steps_var = tk.IntVar(value=1000)
        self.animation_delay_var = tk.IntVar(value=400)
        self.comparison_runs_var = tk.IntVar(value=100)

        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self.reset_board()

    # BUILD THE USER INTERFACE 
    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(root)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))

        board_group = ttk.LabelFrame(left_frame, text="Board")
        board_group.pack(fill=tk.BOTH, expand=False)
        self.board_canvas = tk.Canvas(board_group, width=520, height=520, bg="#ffffff", highlightthickness=0)
        self.board_canvas.pack(padx=8, pady=8)

        anim_group = ttk.LabelFrame(left_frame, text="Animation")
        anim_group.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(anim_group, text="Frame delay (ms):").grid(row=0, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(anim_group, from_=50, to=2000, increment=50, textvariable=self.animation_delay_var, width=6).grid(row=0, column=1, padx=4, pady=6, sticky="w")
        ttk.Button(anim_group, text="Play", command=self.start_animation).grid(row=0, column=2, padx=4, pady=6)
        ttk.Button(anim_group, text="Stop", command=self.stop_animation).grid(row=0, column=3, padx=4, pady=6)
        ttk.Button(anim_group, text="Save GIF...", command=self.save_gif).grid(row=1, column=0, columnspan=2, padx=4, pady=(0, 6), sticky="we")
        ttk.Button(anim_group, text="Reset board", command=self.reset_board).grid(row=1, column=2, columnspan=2, padx=4, pady=(0, 6), sticky="we")

        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        alg_frame = ttk.LabelFrame(right_frame, text="Algorithms")
        alg_frame.pack(fill=tk.X)

        notebook = ttk.Notebook(alg_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        sideways_tab = ttk.Frame(notebook, padding=8)
        notebook.add(sideways_tab, text="Sideways Moves")
        sideways_tab.columnconfigure(0, weight=1)
        sideways_tab.columnconfigure(1, weight=1)

        ttk.Button(sideways_tab, text="Run", command=self.on_run_sideways).grid(row=0, column=0, padx=4, pady=4, sticky="we")
        ttk.Button(sideways_tab, text="Visualize Search", command=self.on_visualize_sideways).grid(row=0, column=1, padx=4, pady=4, sticky="we")
        ttk.Label(sideways_tab, text="Sideways limit").grid(row=1, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(sideways_tab, from_=0, to=500, textvariable=self.sideways_limit_var, width=8).grid(row=1, column=1, padx=4, pady=6, sticky="w")

        restart_tab = ttk.Frame(notebook, padding=8)
        notebook.add(restart_tab, text="Random Restarts")
        restart_tab.columnconfigure(0, weight=1)
        restart_tab.columnconfigure(1, weight=1)

        ttk.Button(restart_tab, text="Run", command=self.on_run_random_restarts).grid(row=0, column=0, padx=4, pady=4, sticky="we")
        ttk.Button(restart_tab, text="Visualize Search", command=self.on_visualize_random_restarts).grid(row=0, column=1, padx=4, pady=4, sticky="we")
        ttk.Checkbutton(restart_tab, text="Allow sideways moves", variable=self.rr_allow_sideways_var).grid(row=1, column=0, columnspan=2, padx=4, pady=6, sticky="w")
        ttk.Label(restart_tab, text="Max moves per restart").grid(row=2, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(restart_tab, from_=1, to=500, textvariable=self.rr_max_moves_var, width=8).grid(row=2, column=1, padx=4, pady=6, sticky="w")
        ttk.Label(restart_tab, text="Max restarts").grid(row=3, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(restart_tab, from_=1, to=500, textvariable=self.rr_max_restarts_var, width=8).grid(row=3, column=1, padx=4, pady=6, sticky="w")

        annealing_tab = ttk.Frame(notebook, padding=8)
        notebook.add(annealing_tab, text="Simulated Annealing")
        annealing_tab.columnconfigure(0, weight=1)
        annealing_tab.columnconfigure(1, weight=1)

        ttk.Button(annealing_tab, text="Run", command=self.on_run_simulated_annealing).grid(row=0, column=0, padx=4, pady=4, sticky="we")
        ttk.Button(annealing_tab, text="Visualize Search", command=self.on_visualize_simulated_annealing).grid(row=0, column=1, padx=4, pady=4, sticky="we")
        ttk.Label(annealing_tab, text="Initial temperature").grid(row=1, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(annealing_tab, from_=10, to=500, increment=10, textvariable=self.annealing_temp_var, width=8).grid(row=1, column=1, padx=4, pady=6, sticky="w")
        ttk.Label(annealing_tab, text="Cooling function").grid(row=2, column=0, padx=4, pady=6, sticky="w")
        ttk.Combobox(annealing_tab, values=("linear", "exponential"), textvariable=self.annealing_cooling_var, state="readonly", width=12).grid(row=2, column=1, padx=4, pady=6, sticky="w")
        ttk.Label(annealing_tab, text="Max steps").grid(row=3, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(annealing_tab, from_=50, to=5000, increment=50, textvariable=self.annealing_steps_var, width=8).grid(row=3, column=1, padx=4, pady=6, sticky="w")

        compare_frame = ttk.LabelFrame(right_frame, text="Comparison")
        compare_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(compare_frame, text="Runs per algorithm").grid(row=0, column=0, padx=4, pady=6, sticky="w")
        ttk.Spinbox(compare_frame, from_=5, to=100, textvariable=self.comparison_runs_var, width=6).grid(row=0, column=1, padx=4, pady=6, sticky="w")
        ttk.Button(compare_frame, text="Run comparison", command=self.on_run_comparison).grid(row=0, column=2, padx=4, pady=6)

        log_frame = ttk.LabelFrame(right_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        self.log_text = tk.Text(log_frame, height=22, state=tk.DISABLED, wrap="word")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scroll.set)

        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

    # RESETS THE BOARD TO A RANDOM STARTING STATE
    def reset_board(self) -> None:
        board = self.problem.initial_board()
        conflicts = self.problem.conflicts(board)
        self.current_algorithm = "Initial board"
        self.current_states = [board.copy()]
        self.current_history = [conflicts]
        self.current_metadata = {}
        self.draw_board(board)
        self._log(f"Reset board. Initial conflicts: {conflicts}\n")
        self._set_status("Ready")

    # UPDATE THE STATUS MESSAGE IN THE UI FOOTER
    def _set_status(self, msg: str) -> None:
        self.status_var.set(msg)

    # LOGS A MESSAGE IN THE LOG
    def _log(self, text: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # DRAWS THE BOARD, QUEENS, CANDIDATE CELLS, AND CONFLICTS ON THE CANVAS
    def draw_board(
        self,
        board: Sequence[int],
        *,
        highlight: Optional[Sequence[Optional[Sequence[int]]]] = None,
        conflicts: Optional[int] = None,
    ) -> None:
        canvas = self.board_canvas
        canvas.delete("all")

        width = int(canvas["width"])
        height = int(canvas["height"])
        n = len(board)
        cell = min(width, height) // n
        offset_x = (width - cell * n) // 2
        offset_y = (height - cell * n) // 2

        moved_from = tuple(highlight[0]) if highlight and highlight[0] else None
        moved_to = tuple(highlight[1]) if highlight and highlight[1] else None

        board_list = list(board)
        candidate_squares = set()
        min_conflict_value: Optional[int] = None

        for col in range(n):
            for row in range(n):
                if board_list[col] == row:
                    continue
                conflicts_if_moved = self.problem.conflicts(self.problem.apply(board_list, (col, row)))
                if min_conflict_value is None or conflicts_if_moved < min_conflict_value:
                    min_conflict_value = conflicts_if_moved
                    candidate_squares = {(row, col)}
                elif conflicts_if_moved == min_conflict_value:
                    candidate_squares.add((row, col))

        for row in range(n):
            for col in range(n):
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                if moved_from == (row, col):
                    color = HIGHLIGHT_FROM
                elif moved_to == (row, col):
                    color = HIGHLIGHT_TO
                elif (row, col) in candidate_squares and board_list[col] != row:
                    color = BEST_CANDIDATE_COLOR

                x0 = offset_x + col * cell
                y0 = offset_y + row * cell
                canvas.create_rectangle(x0, y0, x0 + cell, y0 + cell, fill=color, outline="#2c3e50")

                if board_list[col] != row:
                    conflicts_if_moved = self.problem.conflicts(self.problem.apply(board_list, (col, row)))
                    canvas.create_text(
                        x0 + cell / 2,
                        y0 + cell / 2,
                        text=str(conflicts_if_moved),
                        fill="#1c2833",
                        font=("Helvetica", max(int(cell * 0.28), 10), "bold"),
                    )

        for col, row in enumerate(board_list):
            x0 = offset_x + col * cell
            y0 = offset_y + row * cell
            radius = cell * 0.32
            canvas.create_oval(
                x0 + cell / 2 - radius,
                y0 + cell / 2 - radius,
                x0 + cell / 2 + radius,
                y0 + cell / 2 + radius,
                fill="#17202a",
                outline="#fdfefe",
                width=2,
            )
            canvas.create_text(
                x0 + cell / 2,
                y0 + cell / 2,
                text="Q",
                fill="#fdfefe",
                font=("Helvetica", max(int(cell * 0.45), 14), "bold"),
            )

        if conflicts is not None:
            canvas.create_text(
                width / 2,
                offset_y + cell * n + 16,
                text=f"Conflicts: {conflicts}",
                fill="#1c2833",
                font=("Helvetica", 14, "bold"),
            )

    # STARTS EXECUTING THE SIDEWAYS MOVES ALGORITHM (WITHOUT VISUALIZATION)
    def on_run_sideways(self) -> None:
        self._run_async("Sideways Moves", lambda: self._sideways_worker(False), status="Running Sideways Moves...")

    # STARTS EXECUTING THE SIDEWAYS MOVES ALGORITHM (WITH VISUALIZATION)
    def on_visualize_sideways(self) -> None:
        self._run_async(
            "Sideways Moves",
            lambda: self._sideways_worker(True),
            status="Running Sideways Moves visualization...",
        )

    # STARTS EXECUTING THE RANDOM RESTARTS ALGORITHM (WITHOUT VISUALIZATION)
    def on_run_random_restarts(self) -> None:
        self._run_async(
            "Random Restarts",
            lambda: self._random_restarts_worker(False),
            status="Running Random Restarts...",
        )

    # STARTS EXECUTING THE RANDOM RESTARTS ALGORITHM (WITH VISUALIZATION)
    def on_visualize_random_restarts(self) -> None:
        self._run_async(
            "Random Restarts",
            lambda: self._random_restarts_worker(True),
            status="Running Random Restarts visualization...",
        )

    # STARTS EXECUTING THE SIMULATED ANNEALING ALGORITHM (WITHOUT VISUALIZATION)
    def on_run_simulated_annealing(self) -> None:
        self._run_async(
            "Simulated Annealing",
            lambda: self._annealing_worker(False),
            status="Running Simulated Annealing...",
        )

    # STARTS EXECUTING THE SIMULATED ANNEALING ALGORITHM (WITH VISUALIZATION)
    def on_visualize_simulated_annealing(self) -> None:
        self._run_async(
            "Simulated Annealing",
            lambda: self._annealing_worker(True),
            status="Running Simulated Annealing visualization...",
        )

    # EXECUTES A BACKGROUND FUNCTION USING THREAD AND SCHEDULES CALLBACKS
    def _run_async(self, label: str, worker, *, status: Optional[str] = None) -> None:
        if self._animating:
            self.stop_animation()
        self._set_status(status or f"Running {label}...")
        thread = threading.Thread(target=self._run_worker, args=(label, worker), daemon=True)
        thread.start()

    # WORKER WRAPPER THAT CATCHES EXCEPTIONS AND CALLS CALLBACKS IN THE MAIN THREAD
    def _run_worker(self, label: str, worker) -> None:
        try:
            result = worker()
            self.after(0, lambda: self._on_worker_success(label, result))
        except Exception as exc:
            self.after(0, lambda exc=exc: self._on_worker_failure(label, exc))

    # HANDLES THE WORKER'S SUCCESS RESULT AND UPDATES THE UI AND INTERNAL STATES
    def _on_worker_success(self, label: str, result):
        board, states, history, metadata = result
        history = history or [self.problem.conflicts(board)]
        if not states:
            states = [board.copy()]
        metadata = dict(metadata or {})
        metadata.setdefault("steps", max(len(states) - 1, 0))
        history_series = metadata.get("history_series", history)
        visualize_flag = bool(metadata.get("visualize"))
        display_metadata = {k: v for k, v in metadata.items() if k not in {"history_series", "visualize"}}
        self.current_algorithm = label
        self.current_states = states
        self.current_history = history
        self.current_metadata = metadata
        self._animation_states = states
        self._animation_history = history
        self._animation_index = 0
        highlight = None
        if len(states) >= 2:
            highlight = diff_states(states[-2], states[-1])
        self.draw_board(board, highlight=highlight, conflicts=history[-1] if history else None)
        self._log(self._format_result(label, display_metadata, display_metadata.get("steps", 0)))
        final_conflicts = history[-1] if history else "n/a"
        if visualize_flag:
            self._set_status(f"{label} visualization ready. Final conflicts: {final_conflicts}")
            self._show_history_plot(label, history_series)
        else:
            self._set_status(f"{label} finished. Final conflicts: {final_conflicts}")

    # HANDLES WORKER FAILURES AND DISPLAYS ERROR MESSAGES
    def _on_worker_failure(self, label: str, exc: Exception) -> None:
        self._set_status(f"Failed to run {label}: {exc}")
        messagebox.showerror("Error", f"{label} failed: {exc}")

    # DISPLAY A GRAPH OF CONFLICT HISTORY USING MATPLOTLIB
    def _show_history_plot(self, label: str, history: Sequence[int]) -> None:
        if not history:
            messagebox.showinfo("No data", "No history available for visualization.")
            return
        try:
            plt.figure(figsize=(7.5, 4.2))
            plt.plot(history, marker="o", linewidth=1.4)
            plt.title(f"{label} - Conflicts per step")
            plt.xlabel("Iteration")
            plt.ylabel("Conflicts")
            plt.grid(True, linestyle="--", alpha=0.4)
            plt.tight_layout()
            plt.show()
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to display plot: {exc}")

    # WORKER FOR SIDEWAYS MOVES: EXECUTES THE ALGORITHM AND COLLECTS METRICS
    def _sideways_worker(self, visualize: bool = False):
        limit = self.sideways_limit_var.get()

        def fn():
            return hill_climbing_with_sideways_moves(self.problem, limit, track_states=True)

        result, elapsed_ms, rss_delta, current_bytes, peak_bytes = measure_time_memory(fn)
        board, history, states = result
        board = list(board)
        history = history or [self.problem.conflicts(board)]
        states = states or [board.copy()]

        final_conflicts = history[-1] if history else self.problem.conflicts(board)
        metadata: Dict[str, Any] = {
            "runtime_ms": elapsed_ms,
            "peak_memory_kb": peak_bytes / 1024,
            "steps": max(len(history) - 1, 0),
            "final_conflicts": final_conflicts,
            "sideways_limit": limit,
            "history_series": history.copy(),
            "visualize": visualize,
        }
        if rss_delta:
            metadata["rss_delta_kb"] = rss_delta / 1024
        if current_bytes:
            metadata["current_memory_kb"] = current_bytes / 1024

        return board, states, history, metadata

    # WORKER FOR RANDOM RESTARTS: EXECUTES THE ALGORITHM AND COLLECTS METRICS
    def _random_restarts_worker(self, visualize: bool = False):
        allow_sideways = self.rr_allow_sideways_var.get()
        max_moves = self.rr_max_moves_var.get()
        max_restarts = self.rr_max_restarts_var.get()

        def fn():
            return hill_climbing_with_random_restarts(
                self.problem,
                allow_sideways=allow_sideways,
                max_moves_per_restart=max_moves,
                max_restarts=max_restarts,
                track_states=True,
            )

        result, elapsed_ms, rss_delta, current_bytes, peak_bytes = measure_time_memory(fn)
        board, best_fitness, restart_count, history, states = result
        if board is None:
            board = self.problem.initial_board()
        else:
            board = list(board)
        states = states or [board.copy()]
        history = history or [self.problem.conflicts(board)]
        final_conflicts = self.problem.conflicts(board)
        metadata = {
            "runtime_ms": elapsed_ms,
            "peak_memory_kb": peak_bytes / 1024,
            "steps": max(len(history) - 1, 0),
            "final_conflicts": final_conflicts,
            "restarts": restart_count,
            "allow_sideways": bool(allow_sideways),
            "max_moves_per_restart": max_moves,
            "best_fitness": best_fitness,
            "history_series": history.copy(),
            "visualize": visualize,
        }
        if rss_delta:
            metadata["rss_delta_kb"] = rss_delta / 1024
        if current_bytes:
            metadata["current_memory_kb"] = current_bytes / 1024
        return board, states, history, metadata

    # WORKER FOR SIMULATED ANNEALING: EXECUTES THE ALGORITHM AND COLLECTS METRICS
    def _annealing_worker(self, visualize: bool = False):
        temp = self.annealing_temp_var.get()
        cooling = self.annealing_cooling_var.get()
        max_steps = self.annealing_steps_var.get()
        cooling_id = 1 if cooling.lower().startswith("linear") else 2

        def fn():
            return simulated_annealing(
                self.problem,
                temperature=temp,
                cooling_func=cooling_id,
                track_states=True,
                max_steps=max_steps,
            )

        result, elapsed_ms, rss_delta, current_bytes, peak_bytes = measure_time_memory(fn)
        board, fitness, history, states = result
        board = list(board)
        states = states or [board.copy()]
        history = history or [self.problem.conflicts(board)]
        final_conflicts = self.problem.conflicts(board)
        metadata = {
            "runtime_ms": elapsed_ms,
            "peak_memory_kb": peak_bytes / 1024,
            "steps": max(len(history) - 1, 0),
            "final_conflicts": final_conflicts,
            "fitness": fitness,
            "cooling": cooling,
            "history_series": history.copy(),
            "visualize": visualize,
        }
        if rss_delta:
            metadata["rss_delta_kb"] = rss_delta / 1024
        if current_bytes:
            metadata["current_memory_kb"] = current_bytes / 1024
        return board, states, history, metadata

    # STARTS ANIMATION OF THE CURRENT STATE SEQUENCE
    def start_animation(self) -> None:
        if not self.current_states:
            messagebox.showinfo("No data", "Run an algorithm first.")
            return
        if self._animating:
            return
        self._animating = True
        self._animation_index = 0
        self._animation_states = self.current_states
        self._animation_history = self.current_history
        self._animate_step()
        self._set_status(f"Playing animation for {self.current_algorithm}...")

    # STOPS THE ANIMATION, CLEARS THE RELATED STATE
    def stop_animation(self) -> None:
        if self._anim_after_id:
            self.after_cancel(self._anim_after_id)
        self._anim_after_id = None
        self._animating = False
        self._set_status("Animation stopped")

    # EXECUTES AN ANIMATION STEP, UPDATES THE CANVAS, AND SCHEDULES THE NEXT FRAME
    def _animate_step(self) -> None:
        if not self._animating:
            return
        if not self._animation_states:
            self.stop_animation()
            return
        index = self._animation_index % len(self._animation_states)
        state = self._animation_states[index]
        conflicts = self._animation_history[index] if index < len(self._animation_history) else None
        highlight = None
        if index > 0:
            highlight = diff_states(self._animation_states[index - 1], state)
        self.draw_board(state, highlight=highlight, conflicts=conflicts)
        self._animation_index += 1
        delay = max(self.animation_delay_var.get(), 10)
        self._anim_after_id = self.after(delay, self._animate_step)

    # SAVES A GIF WITH THE CURRENT STATE SEQUENCE AND METADATA
    def save_gif(self) -> None:
        if not self.current_states:
            messagebox.showinfo("No data", "Run an algorithm first.")
            return
        directory = filedialog.askdirectory(title="Select folder to save GIF")
        if not directory:
            return
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{self.current_algorithm.lower().replace(' ', '_')}-{timestamp}.gif"
        path = Path(directory) / filename
        try:
            conflicts = self.current_history if len(self.current_history) == len(self.current_states) else None
            square_conflicts: List[Dict[Tuple[int, int], int]] = []
            best_candidates: List[Set[Tuple[int, int]]] = []
            for state in self.current_states:
                board_list = list(state)
                n = len(board_list)
                state_conflicts: Dict[Tuple[int, int], int] = {}
                best_positions: Set[Tuple[int, int]] = set()
                min_conflict: Optional[int] = None
                for col in range(n):
                    for row in range(n):
                        if board_list[col] == row:
                            continue
                        candidate_board = board_list.copy()
                        candidate_board[col] = row
                        conflict_value = self.problem.conflicts(candidate_board)
                        state_conflicts[(row, col)] = conflict_value
                        if min_conflict is None or conflict_value < min_conflict:
                            min_conflict = conflict_value
                            best_positions = {(row, col)}
                        elif conflict_value == min_conflict:
                            best_positions.add((row, col))
                square_conflicts.append(state_conflicts)
                best_candidates.append(best_positions)
            generate_gif_from_states(
                self.current_states,
                path,
                conflicts=conflicts,
                square_conflicts=square_conflicts,
                best_candidates=best_candidates,
                duration_ms=self.animation_delay_var.get(),
            )
            self._log(f"Saved GIF to {path}\n")
            messagebox.showinfo("GIF saved", f"Animation saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save GIF: {exc}")

    # STARTS THE ALGORITHM COMPARISON TASK (BUTTON)
    def on_run_comparison(self) -> None:
        runs = self.comparison_runs_var.get()
        if runs <= 0:
            messagebox.showinfo("Invalid value", "Number of runs must be positive.")
            return
        self._run_async("Comparison", lambda: self._comparison_worker(runs))

    # COMPARISON WORKER: EXECUTES THE COMPARISON AND COLLECTS METADATA
    def _comparison_worker(self, runs: int):
        def fn():
            return compare_hill_climbing_algorithms(
                num_runs=runs,
                sideways_limits=(10, 100),
                random_max_moves=20,
                random_max_restarts=100,
                annealing_temperature=self.annealing_temp_var.get(),
                annealing_linear_max_steps=self.annealing_steps_var.get(),
                annealing_exp_max_steps=self.annealing_steps_var.get(),
            )

        metrics, elapsed_ms, rss_delta, current_bytes, peak_bytes = measure_time_memory(fn)
        filtered_metrics = {
            key: value
            for key, value in metrics.items()
            if not key.startswith("HillClimbing")
        }
        repo_root = Path(__file__).resolve().parents[2]
        metrics_path = repo_root / "data" / "output" / "metrics" / "metrics_hill_climbing.json"

        if self.current_states:
            board_snapshot = self.current_states[-1].copy()
            states_snapshot = [state.copy() for state in self.current_states]
        else:
            board_snapshot = self.problem.initial_board()
            states_snapshot = [board_snapshot.copy()]

        history_snapshot = list(self.current_history) if self.current_history else [self.problem.conflicts(board_snapshot)]

        metadata = {
            "runtime_ms": elapsed_ms,
            "peak_memory_kb": peak_bytes / 1024,
            "rss_delta_kb": rss_delta / 1024 if rss_delta else 0.0,
            "current_memory_kb": current_bytes / 1024 if current_bytes else 0.0,
            "runs": runs,
            "metrics": filtered_metrics,
            "metrics_path": str(metrics_path),
        }
        return board_snapshot, states_snapshot, history_snapshot, metadata

    # FORMATS THE RESULTS AND METADATA FOR DISPLAY IN THE LOG
    def _format_result(self, label: str, metadata: Dict[str, Any], steps: int) -> str:
        lines = [f"=== {label} ==="]
        lines.append(f"Steps: {steps}")
        if (runs := metadata.get("runs")) is not None:
            lines.append(f"Runs: {runs}")
        if (final_conflicts := metadata.get("final_conflicts")) is not None:
            lines.append(f"Final conflicts: {final_conflicts}")
        if "restarts" in metadata:
            lines.append(f"Restarts: {metadata['restarts']}")
        if "allow_sideways" in metadata:
            lines.append(f"Allow sideways: {metadata['allow_sideways']}")
        if "sideways_limit" in metadata:
            lines.append(f"Sideways limit: {metadata['sideways_limit']}")
        if "max_moves_per_restart" in metadata:
            lines.append(f"Max moves/restart: {metadata['max_moves_per_restart']}")
        if "fitness" in metadata:
            lines.append(f"Fitness: {metadata['fitness']}")
        if "cooling" in metadata:
            lines.append(f"Cooling schedule: {metadata['cooling']}")
        if (runtime := metadata.get("runtime_ms")) is not None:
            lines.append(f"Runtime: {runtime:.2f} ms")
        if (peak := metadata.get("peak_memory_kb")) is not None:
            lines.append(f"Peak memory: {peak:.2f} kB")
        if (rss_delta := metadata.get("rss_delta_kb")) is not None and rss_delta:
            lines.append(f"RSS delta: {rss_delta:.2f} kB")
        if (current_mem := metadata.get("current_memory_kb")) is not None and current_mem:
            lines.append(f"Current memory: {current_mem:.2f} kB")
        if "metrics_path" in metadata:
            lines.append(f"Metrics saved to: {metadata['metrics_path']}")
        if "metrics" in metadata:
            lines.append("-- Metrics snapshot --")
            for key, value in list(metadata["metrics"].items())[:8]:
                lines.append(f"{key}: {value}")
        return "\n".join(lines) + "\n\n"

    # ENSURES THAT THE ANIMATION STOPS WHEN THE APPLICATION IS CLOSED
    def mainloop(self, n: int = 0) -> None:  # type: ignore[override]
        try:
            super().mainloop(n)
        finally:
            self.stop_animation()

# ENTRY POINT: CREATES AND EXECUTES THE APPLICATION
def main() -> None:
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()