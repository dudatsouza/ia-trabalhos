# EXTERNAL IMPORTS
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
import traceback
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PATH CONFIGURATION

# ADJUST SYSTEM PATH TO INCLUDE THE SRC FOLDER FOR MODULE RESOLUTION
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

# INTERNAL PROJECT IMPORTS
# CORE
from core.maze_generator import read_matrix_from_file
from core.maze_representation import Maze
from core.maze_problem import MazeProblem
from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_inadmissible

# SEARCH
from search.measure_time_memory import measure_time_memory

# UNINFORMED SEARCH
from uninformed.dijkstra import dijkstra
from uninformed.best_first_search import reconstruct_path
from uninformed.bidirectional_best_first_search import bidirectional_best_first_search
from uninformed.generate_gifs_uninformed import generate_gifs_uninformed
from uninformed.uninformed_comparison import compare_uninformed_search_algorithms

# INFORMED SEARCH
from informed.a_star_search import a_star_search
from informed.greedy_best_first_search import greedy_best_first_search
from informed.generate_gifs_informed import generate_gifs_informed
from informed.informed_comparison import compare_informed_search_algorithms

# GUI APPLICATION CLASS

# MAIN APPLICATION CLASS FOR THE MAZE SEARCH GUI.
class App(tk.Tk):

    # HANDLES WINDOW CREATION, USER INTERACTIONS, AND ALGORITHM EXECUTION.
    def __init__(self):
        super().__init__()
        self.title("IA - Maze Search (GUI)")
        self.geometry("800x800")

        # --- CORE MAZE AND PROBLEM VARIABLES ---
        self.matrix = None  # STORES THE MAZE LAYOUT AS A LIST OF LISTS
        self.maze = None    # MAZE OBJECT INSTANCE
        self.problem = None # MAZEPROBLEM OBJECT INSTANCE

        # --- FILE PATH CONFIGURATION ---
        # LOCATE THE DEFAULT MAZE FILE RELATIVE TO THIS SCRIPT'S LOCATION
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_maze_path = os.path.join(script_dir, '..', '..', 'data', 'input', 'maze.txt')

        # --- DETECT INFORMED SEARCH IMPLEMENTATIONS ---
        # CHECK IF ALGORITHM FILES EXIST AND ARE NOT EMPTY TO ENABLE/DISABLE BUTTONS
        a_star_path = os.path.join(script_dir, '..', 'informed', 'a_star_search.py')
        greedy_path = os.path.join(script_dir, '..', 'informed', 'greedy_best_first_search.py')
        
        try:
            self.has_a_star = os.path.exists(a_star_path) and os.path.getsize(a_star_path) > 0
        except Exception:
            self.has_a_star = False
            
        try:
            self.has_greedy = os.path.exists(greedy_path) and os.path.getsize(greedy_path) > 0
        except Exception:
            self.has_greedy = False

        # --- VISUALIZATION AND ANIMATION DEFAULTS ---
        self.default_visualize_animate = True       # DEFAULT ANIMATION FLAG (NOT USED DIRECTLY, BUT FOR CLARITY)
        self.default_visualize_use_runtime = True   # ADJUST ANIMATION SPEED BASED ON ALGORITHM RUNTIME
        self.default_playback_multiplier = 6.0      # SLOW DOWN PLAYBACK FOR EASIER OBSERVATION
        self.default_frame_interval_ms = 50         # FALLBACK FRAME INTERVAL IF NOT USING RUNTIME

        # --- ANIMATION CONTROL STATE ---
        self._animating = False             # FLAG TO CHECK IF AN ANIMATION IS CURRENTLY RUNNING
        self._anim_after_id = None          # STORES THE ID OF THE SCHEDULED 'AFTER' CALL FOR CANCELLATION
        self._gif_image_id = None           # (NOT USED) PLACEHOLDER FOR GIF IMAGE HANDLING
        self._last_drawn = {}               # CACHES THE LAST DRAWN STATE ON THE CANVAS

        # --- UI STATE VARIABLES ---
        # STORES THE SELECTED HEURISTIC FOR INFORMED SEARCH VISUALIZATION
        self._viz_informed_heur_var = tk.StringVar(value='manhattan')

        # --- INITIALIZATION ---
        self.create_widgets()
        # ATTEMPT TO SILENTLY LOAD THE DEFAULT MAZE ON STARTUP
        try:
            self.load_maze(self.default_maze_path)
        except Exception as e:
            print(f"Could not load default maze: {e}")

    # CREATES AND PACKS ALL THE MAIN GUI WIDGETS.
    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # --- MAZE FILE SELECTION FRAME ---
        file_frame = ttk.Frame(frm)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="Maze file:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.path_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Reload", command=lambda: self.load_maze(self.path_var.get())).pack(side=tk.LEFT, padx=5)

        # --- MAIN MENU BUTTONS FRAME ---
        menu_frame = ttk.LabelFrame(frm, text="Main Menu")
        menu_frame.pack(fill=tk.X, pady=10)
        ttk.Button(menu_frame, text="Show Maze Initial", command=self.safe_draw_maze).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Stop Animation", command=self.stop_animation).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Uninformed Search", command=self.open_uninformed_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Informed Search", command=self.open_informed_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Show Generated Graph", command=self.open_graph_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Exit", command=self.quit).pack(side=tk.RIGHT, padx=8, pady=6)

        # --- STATUS BAR ---
        status_frame = ttk.Frame(frm)
        status_frame.pack(fill=tk.X, pady=5)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # --- OUTPUT TEXT AREA (LOG) ---
        out_frame = ttk.LabelFrame(frm, text="Activity Log")
        out_frame.pack(fill=tk.BOTH, expand=True)
        self.output = tk.Text(out_frame, height=12)
        self.output.pack(fill=tk.BOTH, expand=True)

        # --- MAZE VISUALIZATION CANVAS ---
        canvas_frame = ttk.LabelFrame(frm, text="Maze View")
        canvas_frame.pack(fill=tk.BOTH, expand=False, pady=6)
        self.canvas = tk.Canvas(canvas_frame, width=600, height=600, bg='black')
        self.canvas.pack()

    # OPENS THE MENU FOR UNINFORMED SEARCH OPTIONS.
    def open_uninformed_window(self):
        w = tk.Toplevel(self)
        w.title("Uninformed Search")
        ttk.Label(w, text="Choose an Uninformed Algorithm:").pack(padx=10, pady=8)
        ttk.Button(w, text="Dijkstra", command=lambda: [w.destroy(), self.run_dijkstra()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Bidirectional Best-First Search", command=lambda: [w.destroy(), self.run_bidirectional()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Comparison of Both", command=lambda: [w.destroy(), self.run_comparison_uninformed()]).pack(fill=tk.X, padx=8, pady=4)
        # THIS BUTTON AUTOMATICALLY GENERATES GIFS IN THE BACKGROUND AND THEN OPENS THE VISUALIZATION WINDOW
        ttk.Button(w, text="Visualize Uninformed Searches", command=lambda: [w.destroy(), self.save_all_uninformed_gifs_and_open_visualizer()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    # OPENS THE WINDOW TO TRIGGER CANVAS VISUALIZATIONS FOR UNINFORMED SEARCHES.
    def open_visualize_uninformed_window(self):
        w = tk.Toplevel(self)
        w.title("Visualize Uninformed")
        ttk.Label(w, text="Choose visualization:").pack(padx=10, pady=8)
        ttk.Button(w, text="Visualize Dijkstra", command=lambda: [w.destroy(), self.visualize_dijkstra()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Visualize Bidirectional", command=lambda: [w.destroy(), self.visualize_bidirectional()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    # OPENS THE MENU FOR INFORMED SEARCH OPTIONS.
    def open_informed_window(self):
        w = tk.Toplevel(self)
        w.title("Informed Search")
        ttk.Label(w, text="Choose an Informed Algorithm:").pack(padx=10, pady=8)
        # APPEND STATUS TO BUTTONS IF ALGORITHM IMPLEMENTATION IS MISSING
        a_star_state = ' (missing)' if not self.has_a_star else ''
        greedy_state = ' (missing)' if not self.has_greedy else ''
        ttk.Button(w, text=f"A* Search{a_star_state}", command=lambda: [w.destroy(), self.open_heuristic_window('A*')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text=f"Greedy Best-First Search{greedy_state}", command=lambda: [w.destroy(), self.open_heuristic_window('Greedy')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Comparison of Both", command=lambda: [w.destroy(), self.run_comparison_informed()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Visualize Informed Searches", command=lambda: [w.destroy(), self.save_all_informed_gifs_and_open_visualizer()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    # OPENS A WINDOW TO SELECT A HEURISTIC FOR AN INFORMED ALGORITHM.
    def open_heuristic_window(self, algorithm: str):
        w = tk.Toplevel(self)
        w.title(f"Heuristics - {algorithm}")
        ttk.Label(w, text=f"Choose heuristic for {algorithm}:").pack(padx=10, pady=8)
        ttk.Button(w, text="Manhattan Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'manhattan')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Euclidean Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'euclidean')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Inadmissible Heuristic", command=lambda: [w.destroy(), self.run_informed(algorithm, 'inadmissible')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    # GENERATES AND DISPLAYS THE MAZE'S GRAPH REPRESENTATION IN A NEW WINDOW.
    def open_graph_window(self):
        if not hasattr(self, 'maze') or not self.maze:
            messagebox.showerror("Error", "Load a maze first!")
            return

        # GENERATE GRAPH FROM MAZE OBJECT
        graph = self.maze.to_graph() if hasattr(self.maze, 'to_graph') else {}
        if not graph:
            messagebox.showinfo("Info", "No graph data available.")
            return

        # CREATE A NEW TOPLEVEL WINDOW FOR THE GRAPH
        graph_window = tk.Toplevel(self)
        graph_window.title("Maze Graph Representation")
        graph_window.geometry("600x600")

        # CREATE MATPLOTLIB FIGURE
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title("Graph Representation of Maze", fontsize=12)
        ax.axis("off")

        # BUILD THE GRAPH USING NETWORKX
        G = nx.Graph()
        for node, neighbors in graph.items():
            for n in neighbors:
                G.add_edge(node, n)

        # POSITION NODES ACCORDING TO THEIR COORDINATES TO RESEMBLE THE MAZE LAYOUT
        pos = {node: (node[1], -node[0]) for node in G.nodes()}
        nx.draw(
            G, pos, ax=ax,
            with_labels=True,
            node_color="#8fd3f4", edge_color="#5dade2",
            node_size=300, font_size=8
        )

        # EMBED THE MATPLOTLIB PLOT INTO THE TKINTER WINDOW
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # OPENS THE WINDOW FOR CANVAS VISUALIZATIONS OF INFORMED SEARCHES.
    def open_visualize_informed_window(self):
        w = tk.Toplevel(self)
        w.title("Visualize Informed")
        ttk.Label(w, text="Choose visualization (Informed):").pack(padx=10, pady=8)

        # HEURISTIC SELECTION
        ttk.Label(w, text="Choose heuristic:").pack(padx=10, pady=(6, 2))
        heur_frame = ttk.Frame(w)
        heur_frame.pack(padx=10, pady=(0, 6))
        ttk.Radiobutton(heur_frame, text="Manhattan", variable=self._viz_informed_heur_var, value='manhattan').pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(heur_frame, text="Euclidean", variable=self._viz_informed_heur_var, value='euclidean').pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(heur_frame, text="Inadmissible", variable=self._viz_informed_heur_var, value='inadmissible').pack(side=tk.LEFT, padx=4)
        
        # VISUALIZATION BUTTONS
        a_star_state = ' (missing)' if not self.has_a_star else ''
        greedy_state = ' (missing)' if not self.has_greedy else ''
        ttk.Button(w, text=f"Visualize A*{a_star_state}", command=lambda: [w.destroy(), self.visualize_a_star()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text=f"Visualize Greedy{greedy_state}", command=lambda: [w.destroy(), self.visualize_greedy()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    # DISPLAYS A SUMMARY OF ALGORITHM RESULTS IN A NEW WINDOW.
    def show_result_summary(self, title: str, metrics: dict):
        w = tk.Toplevel(self)
        w.title(title)
        frm = ttk.Frame(w, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        for i, (k, v) in enumerate(metrics.items()):
            ttk.Label(frm, text=f"{k}:", width=20, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(frm, text=str(v)).grid(row=i, column=1, sticky=tk.W, pady=2)
        ttk.Button(frm, text="Close", command=w.destroy).grid(row=len(metrics), column=0, columnspan=2, pady=10)

    # OPENS A FILE DIALOG TO SELECT A MAZE FILE.
    def browse_file(self):
        p = filedialog.askopenfilename(initialdir=os.path.dirname(self.default_maze_path), filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if p:
            self.path_var.set(p)
            self.load_maze(p)

    # LOADS A MAZE FROM A GIVEN FILE PATH AND UPDATES THE APPLICATION STATE.
    def load_maze(self, path):
        try:
            matrix = read_matrix_from_file(path)
            self.matrix = matrix
            self.maze = Maze(matrix)
            self.problem = MazeProblem(self.maze)
            self.path_var.set(path)
            self.safe_write_output(f"Maze loaded from {path}\nStart: {self.maze.start} - Goal: {self.maze.goal}\n")
            self.safe_draw_maze()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maze: {e}")

    # RETURNS A NEW MAZEPROBLEM WITH START AND GOAL STATES SWAPPED.
    def _create_swapped_problem(self):
        matrix_copy = [row[:] for row in self.matrix]
        for r, row in enumerate(matrix_copy):
            for c, char in enumerate(row):
                if char == 'S':
                    matrix_copy[r][c] = 'G'
                elif char == 'G':
                    matrix_copy[r][c] = 'S'
        swapped_maze = Maze(matrix_copy)
        return MazeProblem(swapped_maze)

    # HELPER TO GATHER ALL UNIQUE 'REACHED' NODES FROM SNAPSHOTS FOR VISUALIZATION.
    def _collect_tree_nodes(self, snapshots):
        nodes = set()
        for snap in snapshots:
            # DIJKSTRA/GREEDY/A* FORMAT
            if 'reached' in snap:
                try:
                    nodes.update(tuple(state) for state in snap['reached'])
                except Exception: pass
            # BIDIRECTIONAL FORMAT
            for key in ('reached_F', 'reached_B'):
                if key in snap:
                    try:
                        nodes.update(tuple(state) for state in snap[key])
                    except Exception: pass
        return nodes

    # STARTS A GIVEN TARGET FUNCTION IN A BACKGROUND DAEMON THREAD.
    def _run_in_thread(self, target, args=()):
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()

    # SCHEDULES WRITING TO THE OUTPUT TEXT WIDGET IN THE MAIN THREAD.
    def safe_write_output(self, text: str):
        self.after(0, lambda: self.write_output(text))

    # SCHEDULES A DRAW_MAZE CALL IN THE MAIN THREAD.
    def safe_draw_maze(self, *args, **kwargs):
        self.after(0, lambda: self.draw_maze(*args, **kwargs))

    # SCHEDULES AN ANIMATE_SNAPSHOTS CALL IN THE MAIN THREAD.
    def safe_animate_snapshots(self, snapshots, interval_ms: int = 100, final_path=None):
        self.after(0, lambda: self.animate_snapshots(snapshots, interval_ms, final_path=final_path))

    # APPENDS TEXT TO THE OUTPUT LOG AND SCROLLS TO THE END.
    def write_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    # STOPS ANY RUNNING ANIMATION SCHEDULED ON THE CANVAS.
    def stop_animation(self):
        self._animating = False
        if self._anim_after_id:
            try:
                self.after_cancel(self._anim_after_id)
            except Exception:
                pass
            self._anim_after_id = None
        # IMPORTANT: DO NOT CLEAR THE CANVAS. LEAVE THE LAST FRAME VISIBLE.

    # DRAWS THE CURRENT MAZE STATE ON THE CANVAS.
    def draw_maze(self, final_path=None, tree_nodes=None, visited=None):
        # - FINAL_PATH: A LIST OF (R, C) TUPLES TO DRAW AS THE FINAL PATH.
        # - TREE_NODES: A SET OF (R, C) TUPLES FOR NODES IN THE SEARCH TREE.
        # - VISITED: A SET OF (R, C) TUPLES FOR ALL VISITED NODES.
        self.canvas.delete('all')
        if not self.matrix:
            return

        rows, cols = len(self.matrix), len(self.matrix[0])
        pad = 2
        
        # CALCULATE CELL SIZE TO FIT THE CANVAS
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_w = max(4, (canvas_w - pad * 2) // max(cols, 1))
        cell_h = max(4, (canvas_h - pad * 2) // max(rows, 1))
        size = min(cell_w, cell_h)

        # COLOR MAPPING FOR DIFFERENT CELL TYPES
        color_map = {'#': 'black', ' ': 'white', 'S': 'green', 'G': 'red'}

        path_set = set(final_path) if final_path else set()
        tree_set = set(tree_nodes) if tree_nodes else set()
        visited_set = set(visited) if visited else set()

        for r in range(rows):
            for c in range(cols):
                char = self.matrix[r][c]
                x0, y0 = pad + c * size, pad + r * size
                x1, y1 = x0 + size, y0 + size
                
                # DRAW BASE CELL
                fill = color_map.get(char, 'white')
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline='gray')

                # DRAW VISITED OVERLAY (IF APPLICABLE)
                if (r, c) in visited_set and char not in ('S', 'G', '#'):
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#8c564b', outline='')
                
                # DRAW SEARCH TREE MARKER (IF APPLICABLE)
                if (r, c) in tree_set and char not in ('S', 'G', '#'):
                    self.canvas.create_oval(x0 + size*0.3, y0 + size*0.3, x1 - size*0.3, y1 - size*0.3, outline='sienna', width=1)
        
        # DRAW FINAL PATH ON TOP
        if final_path:
            for r, c in final_path:
                x0, y0 = pad + c * size, pad + r * size
                x1, y1 = x0 + size, y0 + size
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='lime', outline='lime')
        
        # CACHE THE DRAWN ELEMENTS
        self._last_drawn = {
            'path': list(final_path) if final_path else None,
            'tree': list(tree_nodes) if tree_nodes else None,
            'visited': list(visited_set) if visited_set else None,
        }

    # DRAWS A COLORED RECTANGLE OVER A SPECIFIC CELL (R, C) WITHOUT CLEARING THE CANVAS.
    def _draw_cell_overlay(self, r, c, fill='#add8e6'):
        if not self.matrix: return
        rows, cols = len(self.matrix), len(self.matrix[0])
        pad = 2
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        cell_w = max(4, (canvas_w - pad * 2) // max(cols, 1))
        cell_h = max(4, (canvas_h - pad * 2) // max(rows, 1))
        size = min(cell_w, cell_h)
        x0, y0 = pad + c * size, pad + r * size
        x1, y1 = x0 + size, y0 + size
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline='')

    # ANIMATES A LIST OF SEARCH SNAPSHOTS ON THE CANVAS.
    def animate_snapshots(self, snapshots, interval_ms: int = 100, final_path=None):
        if not snapshots:
            self.safe_draw_maze(final_path=final_path)
            return

        PALETTE = {
            'wall': '#000000', 'free': '#ffffff', 'start': '#2ca02c', 'goal': '#d62728',
            'reached_f': '#1f77b4', 'reached_b': '#ff00ff', 'frontier_f': '#ff7f0e',
            'frontier_b': '#17becf', 'current': '#ffe680', 'path': '#32cd32', 'tree': '#8c564b'
        }

        # PREPARE FRAMES: NORMALIZE SNAPSHOT DATA INTO A CONSISTENT FORMAT
        frames = []
        for snap in snapshots:
            frames.append({
                'reached_F': {tuple(s) for s in snap.get('reached_F', [])},
                'reached_B': {tuple(s) for s in snap.get('reached_B', [])},
                'frontier_F': {tuple(s) for s in snap.get('frontier_F', [])},
                'frontier_B': {tuple(s) for s in snap.get('frontier_B', [])},
                'current': tuple(snap['current']) if snap.get('current') else None,
                'tree': set()
            })

        # CALCULATE ALL VISITED NODES FOR THE FINAL DRAWING
        visited_all = set().union(*(fr['reached_F'] for fr in frames), *(fr['reached_B'] for fr in frames))

        def draw_legend():
            legend_items = [
                ('Wall', PALETTE['wall']), ('Free', PALETTE['free']), ('Start', PALETTE['start']), ('Goal', PALETTE['goal']),
                ('Reached F', PALETTE['reached_f']), ('Reached B', PALETTE['reached_b']), ('Frontier F', PALETTE['frontier_f']),
                ('Frontier B', PALETTE['frontier_b']), ('Current', PALETTE['current']), ('Final Path', PALETTE['path']),
                ('Search Tree', PALETTE['tree'])
            ]
            x0, y0 = self.canvas.winfo_width() - 120, 10
            for i, (name, color) in enumerate(legend_items):
                y = y0 + i * 20
                self.canvas.create_rectangle(x0, y, x0 + 15, y + 15, fill=color)
                self.canvas.create_text(x0 + 20, y + 7, anchor='w', text=name, font=('Arial', 10), fill='white')

        # CANCEL PREVIOUS ANIMATION
        self.stop_animation()
        self._animating = True

        # PLAYBACK LOOP
        def play(idx=0):
            if not self._animating:
                return

            if idx >= len(frames):
                # DRAW THE FINAL STATE WITH THE PATH AND ALL VISITED NODES
                self.draw_maze(final_path=final_path, visited=visited_all)
                draw_legend()
                self._animating = False
                return

            f = frames[idx]
            # DRAW THE BASE MAZE WITHOUT OVERLAYS
            self.draw_maze(tree_nodes=f.get('tree'))
            
            # DRAW OVERLAYS FOR THE CURRENT FRAME
            for r, c in f['reached_F']: self._draw_cell_overlay(r, c, fill=PALETTE['reached_f'])
            for r, c in f['reached_B']: self._draw_cell_overlay(r, c, fill=PALETTE['reached_b'])
            for r, c in f['frontier_F']: self._draw_cell_overlay(r, c, fill=PALETTE['frontier_f'])
            for r, c in f['frontier_B']: self._draw_cell_overlay(r, c, fill=PALETTE['frontier_b'])
            if f['current']:
                r, c = f['current']
                self._draw_cell_overlay(r, c, fill=PALETTE['current'])

            draw_legend()
            
            # SCHEDULE THE NEXT FRAME
            self._anim_after_id = self.after(max(1, interval_ms), lambda: play(idx + 1))

        play(0)

    # RUNS THE DIJKSTRA ALGORITHM, MEASURES METRICS, AND TRIGGERS ANIMATION.
    def run_dijkstra(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Running Dijkstra...\n")
            
            # 1. MEASURE PERFORMANCE: RUN WITHOUT CALLBACKS TO GET ACCURATE METRICS
            try:
                result, elapsed_time, memory_used, _, _ = measure_time_memory(dijkstra, self.problem, None)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                goal_node, nodes_expanded = result
                path = reconstruct_path(goal_node) if goal_node else None
            except Exception as e:
                self.safe_write_output(f"Error during Dijkstra measurement: {e}\n")
                return

            # 2. COLLECT SNAPSHOTS: RE-RUN THE ALGORITHM TO CAPTURE VISUALIZATION FRAMES
            snapshots = []
            def on_step_collect(snapshot):
                snap_copy = {
                    'reached_F': [tuple(n) for n in snapshot.get('reached', [])], 'reached_B': [],
                    'frontier_F': [tuple(n) for n in snapshot.get('frontier', [])], 'frontier_B': [],
                    'current': tuple(snapshot['current']) if 'current' in snapshot else None
                }
                snapshots.append(snap_copy)
            try:
                dijkstra(self.problem, on_step=on_step_collect)
            except Exception: pass # CONTINUE EVEN IF SNAPSHOT COLLECTION FAILS

            # 3. ANIMATE AND DISPLAY RESULTS
            # CALCULATE ANIMATION INTERVAL BASED ON THE MEASURED TIME
            frames = len(snapshots) or 1
            mult = self.default_playback_multiplier
            if self.default_visualize_use_runtime:
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
            else:
                interval_ms = self.default_frame_interval_ms
            
            self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
            
            # DISPLAY MEASURED METRICS
            metrics = {
                'Status': 'Path found' if goal_node else 'No path', 'Path length': len(path) if path else 0,
                'Cost': getattr(goal_node, 'g', 'N/A'), 'Nodes expanded': nodes_expanded,
                'Time (ms)': f"{elapsed_time:.3f}", 'Memory (B)': f"{memory_used:.3f}",
            }
            self.after(0, lambda: self.show_result_summary('Dijkstra - Result', metrics))
            self.safe_write_output(f"Dijkstra complete. Time: {elapsed_time:.3f} ms, Memory: {memory_used:.3f} B\n")

        self._run_in_thread(worker)

    # RUNS THE BIDIRECTIONAL SEARCH, MEASURES METRICS, AND TRIGGERS ANIMATION.
    def run_bidirectional(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Running Bidirectional Best-First Search...\n")
            
            # 1. PREPARE & MEASURE
            problem_2 = self._create_swapped_problem()
            def run_call_no_cb():
                return bidirectional_best_first_search(self.problem, lambda n: n.g, problem_2, lambda n: n.g)

            try:
                result, elapsed_time, memory_used, _, _ = measure_time_memory(run_call_no_cb)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None
            except Exception as e:
                self.safe_write_output(f"Error during Bidirectional measurement: {e}\n")
                return

            # 2. COLLECT SNAPSHOTS
            snapshots = []
            def on_step_collect(snapshot): snapshots.append(snapshot.copy())
            try:
                bidirectional_best_first_search(self.problem, lambda n: n.g, problem_2, lambda n: n.g, on_step=on_step_collect)
            except Exception: pass

            # 3. ANIMATE AND DISPLAY RESULTS
            frames = len(snapshots) or 1
            mult = self.default_playback_multiplier
            if self.default_visualize_use_runtime:
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
            else:
                interval_ms = self.default_frame_interval_ms
            
            self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)

            metrics = {
                'Status': 'Path found' if solution else 'No path', 'Path length': len(path) if path else 0,
                'Cost': getattr(solution, 'g', 'N/A'), 'Nodes expanded': nodes_expanded,
                'Time (ms)': f"{elapsed_time:.3f}", 'Memory (B)': f"{memory_used:.3f}",
            }
            self.after(0, lambda: self.show_result_summary('Bidirectional - Result', metrics))
            self.safe_write_output(f"Bidirectional complete. Time: {elapsed_time:.3f} ms, Memory: {memory_used:.3f} B\n")

        self._run_in_thread(worker)

    # GENERIC RUNNER FOR INFORMED SEARCH ALGORITHMS.
    def run_informed(self, algorithm: str, heuristic: str):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output(f"Running {algorithm} with {heuristic} heuristic...\n")

        if algorithm == 'A*':
            self.run_a_star(heuristic)
        elif algorithm == 'Greedy':
            self.run_greedy(heuristic)

    # RUNS THE A* ALGORITHM WITH A GIVEN HEURISTIC.
    def run_a_star(self, heuristic: str = 'manhattan'):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            try:
                h_map = {'manhattan': h_manhattan_distance, 'euclidean': h_euclidean_distance, 'inadmissible': h_inadmissible}
                h_fn = h_map.get(heuristic, h_manhattan_distance)

                # 1. MEASURE PERFORMANCE
                def run_call_measure(): return a_star_search(self.problem, h_fn)
                result, elapsed_time, memory_used, _, _ = measure_time_memory(run_call_measure)
                if not result:
                    self.after(0, lambda: self.show_result_summary(f"A* Result", {'Status': 'No path found'}))
                    return
                goal, nodes_expanded = result
                path = reconstruct_path(goal) if goal else None

                # 2. COLLECT SNAPSHOTS
                snapshots = []
                def on_step(snapshot):
                    snap_copy = {
                        'reached_F': [tuple(s) for s in snapshot.get('reached', [])], 'reached_B': [],
                        'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])], 'frontier_B': [],
                        'current': tuple(snapshot['current']) if 'current' in snapshot else None
                    }
                    snapshots.append(snap_copy)
                try:
                    a_star_search(self.problem, h_fn, on_step=on_step)
                except Exception: pass

                # 3. ANIMATE AND DISPLAY RESULTS
                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                
                metrics = {
                    'Status': 'Path found' if goal else 'No path', 'Path length': len(path) if path else 0,
                    'Cost': getattr(goal, 'g', 'N/A'), 'Nodes expanded': nodes_expanded,
                    'Time (ms)': f"{elapsed_time:.3f}", 'Memory (B)': f"{memory_used:.3f}",
                }
                self.after(0, lambda: self.show_result_summary(f"A* - {heuristic}", metrics))
                self.safe_write_output(f"A* ({heuristic}) complete. Time: {elapsed_time:.3f} ms, Memory: {memory_used:.3f} B\n")

            except Exception as e:
                self.safe_write_output(f"Error running A*: {e}\n")

        self._run_in_thread(worker)

    # RUNS THE GREEDY BEST-FIRST SEARCH ALGORITHM WITH A GIVEN HEURISTIC.
    def run_greedy(self, heuristic: str = 'manhattan'):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            try:
                h_map = {'manhattan': h_manhattan_distance, 'euclidean': h_euclidean_distance, 'inadmissible': h_inadmissible}
                heuristic_fn = h_map.get(heuristic, h_manhattan_distance)
                
                # PRE-CALCULATE HEURISTIC VALUES FOR ALL NODES
                heuristic_table = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=heuristic_fn)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }

                # 1. MEASURE PERFORMANCE
                def run_call_measure(): return greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table)
                result, elapsed_time, memory_used, _, _ = measure_time_memory(run_call_measure)
                if not result:
                    self.after(0, lambda: self.show_result_summary(f"Greedy Result", {'Status':'No path found'}))
                    return
                goal, nodes_expanded = result
                path = reconstruct_path(goal) if goal else None

                # 2. COLLECT SNAPSHOTS
                snapshots = []
                def on_step(snapshot):
                    snap_copy = {
                        'reached_F': [tuple(s) for s in snapshot.get('reached', [])], 'reached_B': [],
                        'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])], 'frontier_B': [],
                        'current': tuple(snapshot['current']) if 'current' in snapshot else None
                    }
                    snapshots.append(snap_copy)
                try:
                    greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table, on_step=on_step)
                except Exception: pass
                
                # 3. ANIMATE AND DISPLAY RESULTS
                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                
                metrics = {
                    'Status': 'Path found' if goal else 'No path', 'Path length': len(path) if path else 0,
                    'Cost': getattr(goal, 'g', 'N/A'), 'Nodes expanded': nodes_expanded,
                    'Time (ms)': f"{elapsed_time:.3f}", 'Memory (B)': f"{memory_used:.3f}",
                }
                self.after(0, lambda: self.show_result_summary(f"Greedy - {heuristic}", metrics))
                self.safe_write_output(f"Greedy ({heuristic}) complete. Time: {elapsed_time:.3f} ms, Memory: {memory_used:.3f} B\n")

            except Exception as e:
                self.safe_write_output(f"Error running Greedy: {e}\n")

        self._run_in_thread(worker)

    # RUNS A BENCHMARK COMPARISON BETWEEN UNINFORMED ALGORITHMS.
    def run_comparison_uninformed(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output("Running uninformed comparison (15 runs each)...\n")

        def worker():
            try:
                metrics = compare_uninformed_search_algorithms(self.matrix)
            except Exception as e:
                self.safe_write_output(f"Error during uninformed comparison: {e}\n")
                return

            def show_table(title, metrics_data):
                win = Toplevel(self)
                win.title(title)
                win.geometry("500x320")
                tree = ttk.Treeview(win, columns=("Metric", "Dijkstra", "Bidirectional"), show='headings')
                tree.heading("Metric", text="Metric")
                tree.heading("Dijkstra", text="Dijkstra")
                tree.heading("Bidirectional", text="Bidirectional")
                tree.column("Metric", width=150, anchor='w')
                tree.column("Dijkstra", width=150, anchor='center')
                tree.column("Bidirectional", width=150, anchor='center')

                metric_map = [
                    ("Avg Time (ms)", 'Dijkstra avg time (ms)', 'Bidirectional avg time (ms)'),
                    ("Avg Nodes", 'Dijkstra avg nodes', 'Bidirectional avg nodes'),
                    ("Avg Cost", 'Dijkstra avg cost', 'Bidirectional avg cost'),
                    ("Avg Peak Memory (KB)", 'Dijkstra avg peak (KB)', 'Bidirectional avg peak (KB)'),
                    ("Avg Current Memory (KB)", 'Dijkstra avg current (KB)', 'Bidirectional avg current (KB)'),
                    ("Avg RSS Memory (B)", 'Dijkstra avg memory (B)', 'Bidirectional avg memory (B)'),
                    ("Solutions Found", 'Dijkstra found count', 'Bidirectional found count')
                ]
                for row_name, key_d, key_b in metric_map:
                    tree.insert("", "end", values=(row_name, metrics_data[key_d], metrics_data[key_b]))

                tree.pack(expand=True, fill='both', padx=10, pady=10)

            self.after(0, lambda: show_table('Comparison - Uninformed Algorithms', metrics))

        self._run_in_thread(worker)

    # RUNS A BENCHMARK COMPARISON BETWEEN INFORMED ALGORITHMS.
    def run_comparison_informed(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output("Running informed comparison (15 runs each if available)...\n")

        def worker():
            try:
                metrics = compare_informed_search_algorithms(self.matrix, num_runs=15)
            except Exception as e:
                self.safe_write_output(f"Error during informed comparison: {e}\n")
                return
            
            def show_table(title, metrics_data):
                win = Toplevel(self)
                win.title(title)
                win.geometry("1050x380")
                cols = ("Metric", "A*-Manhattan", "A*-Euclidean", "A*-Inadmissible",
                        "Greedy-Manhattan", "Greedy-Euclidean", "Greedy-Inadmissible")
                tree = ttk.Treeview(win, columns=cols, show='headings')
                for col in cols: tree.heading(col, text=col)
                tree.column("Metric", width=140, anchor='w')
                for col in cols[1:]: tree.column(col, width=110, anchor='center')
                
                metric_keys = [
                    ("Avg Time (ms)", "avg time (ms)"), ("Avg Nodes", "avg nodes"), ("Avg Cost", "avg cost"),
                    ("Avg Peak Memory (KB)", "avg peak (KB)"), ("Avg Current Memory (KB)", "avg current (KB)"),
                    ("Avg RSS Memory (B)", "avg memory (B)"), ("Solutions Found", "found count")
                ]
                alg_keys = ["A*-Manhattan", "A*-Euclidean", "A*-Inadmissible", "Greedy-Manhattan", "Greedy-Euclidean", "Greedy-Inadmissible"]
                
                for row_name, key_suffix in metric_keys:
                    values = [row_name] + [metrics_data[f'{alg_key} {key_suffix}'] for alg_key in alg_keys]
                    tree.insert("", "end", values=values)

                tree.pack(expand=True, fill='both', padx=10, pady=10)

            self.after(0, lambda: show_table('Comparison - Informed Algorithms', metrics))

        self._run_in_thread(worker)

    # RUNS DIJKSTRA PURELY FOR VISUALIZATION ON THE CANVAS.
    def visualize_dijkstra(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Visualizing Dijkstra...\n")
            snapshots = []

            def on_step(snapshot):
                snap_copy = {
                    'reached_F': [tuple(n) for n in snapshot.get('reached', [])], 'reached_B': [],
                    'frontier_F': [tuple(n) for n in snapshot.get('frontier', [])], 'frontier_B': [],
                    'current': tuple(snapshot['current']) if 'current' in snapshot else None
                }
                snapshots.append(snap_copy)

            try:
                result, elapsed_time, _, _, _ = measure_time_memory(dijkstra, self.problem, on_step=on_step)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                solution, _ = result
                path = reconstruct_path(solution) if solution else None
                
                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                self.safe_write_output("Animation played in GUI.\n")
            except Exception as e:
                self.safe_write_output(f"Error visualizing Dijkstra: {e}\n")

        self._run_in_thread(worker)

    # RUNS BIDIRECTIONAL SEARCH PURELY FOR VISUALIZATION ON THE CANVAS.
    def visualize_bidirectional(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Visualizing Bidirectional...\n")
            snapshots = []
            def on_step(snapshot): snapshots.append(snapshot.copy())

            try:
                problem_2 = self._create_swapped_problem()
                def run_call():
                    return bidirectional_best_first_search(self.problem, lambda n: n.g, problem_2, lambda n: n.g, on_step=on_step)
                result, elapsed_time, _, _, _ = measure_time_memory(run_call)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                solution, _ = result
                path = reconstruct_path(solution) if solution else None

                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                self.safe_write_output("Animation played in GUI.\n")
            except Exception as e:
                self.safe_write_output(f"Error visualizing Bidirectional: {e}\n")

        self._run_in_thread(worker)

    # RUNS A* PURELY FOR VISUALIZATION ON THE CANVAS.
    def visualize_a_star(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        if not self.has_a_star:
            messagebox.showinfo("Not available", "A* implementation not present.")
            return

        def worker():
            self.safe_write_output("Visualizing A*...\n")
            snapshots = []

            def on_step(snapshot):
                snap_copy = {
                    'reached_F': [tuple(s) for s in snapshot.get('reached', [])], 'reached_B': [],
                    'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])], 'frontier_B': [],
                    'current': tuple(snapshot['current']) if 'current' in snapshot else None
                }
                snapshots.append(snap_copy)

            try:
                choice = self._viz_informed_heur_var.get()
                h_map = {'manhattan': h_manhattan_distance, 'euclidean': h_euclidean_distance, 'inadmissible': h_inadmissible}
                h_fn = h_map.get(choice, h_manhattan_distance)
                
                def run_call(): return a_star_search(self.problem, h_fn, on_step=on_step)
                result, elapsed_time, _, _, _ = measure_time_memory(run_call)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                solution, _ = result
                path = reconstruct_path(solution) if solution else None

                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                self.safe_write_output("Animation played in GUI.\n")
            except Exception as e:
                self.safe_write_output(f"Error visualizing A*: {e}\n")

        self._run_in_thread(worker)

    # RUNS GREEDY SEARCH PURELY FOR VISUALIZATION ON THE CANVAS.
    def visualize_greedy(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        if not self.has_greedy:
            messagebox.showinfo("Not available", "Greedy implementation not present.")
            return

        def worker():
            self.safe_write_output("Visualizing Greedy Best-First Search...\n")
            snapshots = []

            def on_step(snapshot):
                snap_copy = {
                    'reached_F': [tuple(s) for s in snapshot.get('reached', [])], 'reached_B': [],
                    'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])], 'frontier_B': [],
                    'current': tuple(snapshot['current']) if 'current' in snapshot else None
                }
                snapshots.append(snap_copy)

            try:
                choice = self._viz_informed_heur_var.get()
                h_map = {'manhattan': h_manhattan_distance, 'euclidean': h_euclidean_distance, 'inadmissible': h_inadmissible}
                heuristic_fn = h_map.get(choice, h_manhattan_distance)
                
                heuristic_table = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=heuristic_fn)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }

                def run_call(): return greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table, on_step=on_step)
                result, elapsed_time, _, _, _ = measure_time_memory(run_call)
                if not result:
                    self.safe_write_output("No path found\n")
                    return
                solution, _ = result
                path = reconstruct_path(solution) if solution else None

                frames, mult = len(snapshots) or 1, self.default_playback_multiplier
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult)) if self.default_visualize_use_runtime else self.default_frame_interval_ms
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                self.safe_write_output("Animation played in GUI.\n")
            except Exception as e:
                self.safe_write_output(f"Error visualizing Greedy: {e}\n")

        self._run_in_thread(worker)

    # SAVES GIFS FOR ALL UNINFORMED SEARCHES AND OPENS THE VISUALIZE WINDOW.
    def save_all_uninformed_gifs_and_open_visualizer(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        # OPEN THE VISUALIZATION WINDOW IMMEDIATELY SO THE USER CAN INTERACT
        self.open_visualize_uninformed_window()

        def worker():
            try:
                self.safe_write_output("Auto-saving uninformed GIFs (Dijkstra/Bidirectional)...\n")
                
                # DEFINE OUTPUT DIRECTORY
                try:
                    repo_root = Path(__file__).resolve().parents[2]
                except Exception:
                    repo_root = Path.cwd() # FALLBACK
                output_dir = repo_root / 'data' / 'output' / 'visualization' / 'uninformed'
                output_dir.mkdir(parents=True, exist_ok=True)
                self.safe_write_output(f"Output directory: {output_dir}\n")

                # GENERATE GIFS
                results = []
                for alg in ['dijkstra', 'bidirectional']:
                    out_path = output_dir / f'visualization-{alg}.gif'
                    try:
                        self.safe_write_output(f"Generating {alg} GIF -> {out_path}...\n")
                        res = generate_gifs_uninformed(self.problem, self.matrix, alg, 100, str(out_path))
                        if res and Path(res).exists():
                            self.safe_write_output(f"Saved: {res}\n")
                            results.append((alg, True))
                        else:
                            self.safe_write_output(f"No output for {alg}\n")
                            results.append((alg, False))
                    except Exception as e:
                        self.safe_write_output(f"Error generating {alg} GIF: {e}\n{traceback.format_exc()}\n")
                        results.append((alg, False))

                ok_count = sum(1 for _, success in results if success)
                self.safe_write_output(f"Auto-save complete: {ok_count}/{len(results)} GIFs saved.\n")
            except Exception as e:
                self.safe_write_output(f"Error in uninformed auto-save worker: {e}\n{traceback.format_exc()}\n")

        self._run_in_thread(worker)

    # SAVES GIFS FOR ALL INFORMED SEARCHES/HEURISTICS AND OPENS THE VISUALIZE WINDOW.
    def save_all_informed_gifs_and_open_visualizer(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        # OPEN THE VISUALIZATION WINDOW IMMEDIATELY
        self.open_visualize_informed_window()

        def worker():
            try:
                self.safe_write_output("Auto-saving informed GIFs (A*/Greedy for all heuristics)...\n")            
                
                # DEFINE OUTPUT DIRECTORY
                try:
                    repo_root = Path(__file__).resolve().parents[2]
                except Exception:
                    repo_root = Path.cwd() # FALLBACK
                output_dir = repo_root / 'data' / 'output' / 'visualization' / 'informed'
                output_dir.mkdir(parents=True, exist_ok=True)
                self.safe_write_output(f"Output directory: {output_dir}\n")

                # GENERATE GIFS
                combos = [
                    ('a_star', 'manhattan'), ('a_star', 'euclidean'), ('a_star', 'inadmissible'),
                    ('greedy', 'manhattan'), ('greedy', 'euclidean'), ('greedy', 'inadmissible'),
                ]
                results = []
                for alg, heur in combos:
                    out_path = output_dir / f'visualization-{alg}-{heur}.gif'
                    try:
                        self.safe_write_output(f"Generating {alg} with {heur} -> {out_path}...\n")
                        res = generate_gifs_informed(self.problem, self.matrix, heur, alg, 100, str(out_path))
                        if res and Path(res).exists():
                            self.safe_write_output(f"Saved: {res}\n")
                            results.append((f"{alg}-{heur}", True))
                        else:
                            self.safe_write_output(f"No output for {alg} {heur}\n")
                            results.append((f"{alg}-{heur}", False))
                    except Exception as e:
                        self.safe_write_output(f"Error generating {alg} {heur}: {e}\n{traceback.format_exc()}\n")
                        results.append((f"{alg}-{heur}", False))

                ok_count = sum(1 for _, success in results if success)
                self.safe_write_output(f"Auto-save complete: {ok_count}/{len(results)} GIFs saved.\n")
            except Exception as e:
                self.safe_write_output(f"Error in informed auto-save worker: {e}\n{traceback.format_exc()}\n")

        self._run_in_thread(worker)


# SCRIPT EXECUTION
if __name__ == '__main__':
    app = App()
    app.mainloop()
