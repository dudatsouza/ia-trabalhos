import os
import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

# Try to import project modules using the new package layout. If imports fail,
# the GUI will still be created but action buttons that rely on the code will
# produce errors when invoked.
try:
    from core.maze_generator import read_matrix_from_file
    from core.maze_representation import Maze
    from core.maze_problem import MazeProblem
    from search.measure_time_memory import measure_time_memory
    from uninformed.dijkstra import dijkstra
    from uninformed.bidirectional_best_first_search import bidirectional_best_first_search
    from search.best_first_search import reconstruct_path
    import search.visualize_matrix as visualize_matrix
except Exception as e:
    print("Warning: imports failed in run_gui.py:", e)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IA - Busca em Labirinto (GUI)")
        self.geometry("800x800")

        # Locate maze file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # script_dir is src/tools; data is at repo_root/data/input/maze.txt -> go up two dirs
        self.default_maze_path = os.path.join(script_dir, '..', '..', 'data', 'input', 'maze-9.txt')
        self.matrix = None
        self.maze = None
        self.problem = None

        # detect informed search implementations (file-system based relative check)
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

        # default visualization options (always animate in GUI using runtime speed)
        self.default_visualize_animate = True
        self.default_visualize_use_runtime = True
        # make default playback slower for easier observation
        self.default_playback_multiplier = 6.0
        # fallback fixed interval (ms) when not using runtime-based speed
        self.default_frame_interval_ms = 50

        # animation control state
        self._animating = False
        self._anim_after_id = None
        self._gif_image_id = None
        self._last_drawn = {}

        # informed visualization heuristic selection (manhattan|euclidean|octile|chebyshev)
        self._viz_informed_heur_var = tk.StringVar(value='manhattan')

        self.create_widgets()
        # attempt to load default maze silently; if fails show error
        try:
            self.load_maze(self.default_maze_path)
        except Exception as e:
            print(f"Could not load default maze: {e}")

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Maze file selection
        file_frame = ttk.Frame(frm)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="Maze file:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.path_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Reload", command=lambda: self.load_maze(self.path_var.get())).pack(side=tk.LEFT, padx=5)

        # Main menu (several small windows will open based on choice)
        menu_frame = ttk.LabelFrame(frm, text="Main Menu")
        menu_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(menu_frame, text="Show Maze Initial", command=self.safe_draw_maze).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Stop Animation", command=self.stop_animation).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Uninformed Search", command=self.open_uninformed_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Informed Search", command=self.open_informed_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Show Generated Graph", command=self.open_graph_window).pack(side=tk.LEFT, padx=8, pady=6)
        ttk.Button(menu_frame, text="Exit", command=self.quit).pack(side=tk.RIGHT, padx=8, pady=6)

        # High-level summary area (single-line status)
        status_frame = ttk.Frame(frm)
        status_frame.pack(fill=tk.X, pady=5)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # Output text (kept for logs but not primary UX)
        out_frame = ttk.LabelFrame(frm, text="Activity Log")
        out_frame.pack(fill=tk.BOTH, expand=True)
        self.output = tk.Text(out_frame, height=12)
        self.output.pack(fill=tk.BOTH, expand=True)

        # Maze visual canvas on the right
        canvas_frame = ttk.LabelFrame(frm, text="Maze View")
        canvas_frame.pack(fill=tk.BOTH, expand=False, pady=6)
        self.canvas = tk.Canvas(canvas_frame, width=600, height=600, bg='black')
        self.canvas.pack()

    # --- Thread-safe UI helpers ---
    def safe_write_output(self, text: str):
        """Schedule writing to the text widget in the main thread."""
        self.after(0, lambda: self.write_output(text))

    def safe_draw_maze(self, *args, **kwargs):
        """Schedule draw_maze call in the main thread."""
        self.after(0, lambda: self.draw_maze(*args, **kwargs))

    def safe_animate_snapshots(self, snapshots, interval_ms: int = 100, final_path=None):
        """Schedule animate_snapshots call in the main thread."""
        self.after(0, lambda: self.animate_snapshots(snapshots, interval_ms, final_path=final_path))

    def stop_animation(self):
        """Stop any running animation scheduled on the canvas."""
        # flip flag and cancel scheduled after callback if present
        try:
            # stop playback loop — subsequent scheduled callbacks will be ignored/cancelled
            self._animating = False
            if getattr(self, '_anim_after_id', None):
                try:
                    self.after_cancel(self._anim_after_id)
                except Exception:
                    pass
                self._anim_after_id = None
            # IMPORTANT: don't delete or redraw canvas here. Keep the current frame visible
            # so 'Stop' leaves the visualization exactly where it was.
        except Exception:
            pass

    # --- Window helpers for menus ---
    def open_uninformed_window(self):
        w = tk.Toplevel(self)
        w.title("Uninformed Search")
        ttk.Label(w, text="Choose an Uninformed Algorithm:").pack(padx=10, pady=8)
        ttk.Button(w, text="Dijkstra", command=lambda: [w.destroy(), self.run_dijkstra()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Bidirectional Best-First Search", command=lambda: [w.destroy(), self.run_bidirectional()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Comparison of Both", command=lambda: [w.destroy(), self.run_comparison_uninformed()]).pack(fill=tk.X, padx=8, pady=4)
        
        # --- LINHA MODIFICADA ---
        # O comando agora chama a nova função que gera GIFs em background
        ttk.Button(
            w,
            text="Visualize Uninformed Searches",
            command=lambda: [w.destroy(), self.save_all_uninformed_gifs_and_open_visualizer()]
        ).pack(fill=tk.X, padx=8, pady=4)
        # --- FIM DA MODIFICAÇÃO ---

        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    def open_visualize_uninformed_window(self):
        w = tk.Toplevel(self)
        w.title("Visualize Uninformed")
        ttk.Label(w, text="Choose visualization:").pack(padx=10, pady=8)
        ttk.Button(w, text="Visualize Dijkstra", command=lambda: [w.destroy(), self.visualize_dijkstra()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Visualize Bidirectional", command=lambda: [w.destroy(), self.visualize_bidirectional()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    def open_informed_window(self):
        w = tk.Toplevel(self)
        w.title("Informed Search")
        ttk.Label(w, text="Choose an Informed Algorithm:").pack(padx=10, pady=8)
        a_star_state = ' (missing)' if not self.has_a_star else ''
        greedy_state = ' (missing)' if not self.has_greedy else ''
        ttk.Button(w, text=f"A* Search{a_star_state}", command=lambda: [w.destroy(), self.open_heuristic_window('A*')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text=f"Greedy Best-First Search{greedy_state}", command=lambda: [w.destroy(), self.open_heuristic_window('Greedy')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Comparison of A* and Greedy", command=lambda: [w.destroy(), self.run_comparison_informed()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Comparison of Heuristics", command=lambda: [w.destroy(), self.run_heuristics_comparison()]).pack(fill=tk.X, padx=8, pady=4)
        # When the user requests to visualize informed searches, first auto-save
        # all 4 GIFs in background (A*/Greedy × Manhattan/Euclidean/Octile/Chebyshev), then open
        # the visualize window for canvas playback. This keeps the UI simple: the
        # visualize window only contains playback actions.
        ttk.Button(
            w,
            text="Visualize Informed Searches",
            command=lambda: [w.destroy(), self.save_all_informed_gifs_and_open_visualizer()]
        ).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    def open_heuristic_window(self, algorithm: str):
        w = tk.Toplevel(self)
        w.title(f"Heuristics - {algorithm}")
        ttk.Label(w, text=f"Choose heuristic for {algorithm}:").pack(padx=10, pady=8)
        ttk.Button(w, text="Manhattan Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'manhattan')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Euclidean Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'euclidean')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Octile Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'octile')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Chebyshev Distance", command=lambda: [w.destroy(), self.run_informed(algorithm, 'chebyshev')]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    def open_graph_window(self):
        import networkx as nx
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        if not hasattr(self, 'maze') or not self.maze:
            messagebox.showerror("Error", "Load a maze first!")
            return

        # Cria o grafo
        graph = self.maze.to_graph() if hasattr(self.maze, 'to_graph') else {}
        if not graph:
            messagebox.showinfo("Info", "No graph data available.")
            return

        # Cria nova janela
        graph_window = tk.Toplevel(self)
        graph_window.title("Maze Graph Representation")
        graph_window.geometry("600x600")

        # Cria figura matplotlib
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_title("Graph Representation of Maze", fontsize=12)
        ax.axis("off")

        # Monta o grafo
        G = nx.Graph()
        for node, neighbors in graph.items():
            for n in neighbors:
                G.add_edge(node, n)

        # Posição dos nós conforme as coordenadas (para parecer o labirinto)
        pos = {node: (node[1], -node[0]) for node in G.nodes()}
        nx.draw(
            G, pos, ax=ax,
            with_labels=True,
            node_color="#8fd3f4", edge_color="#5dade2",
            node_size=300, font_size=8
        )

        # Embute o gráfico no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # --- High level result UI ---
    def show_result_summary(self, title: str, metrics: dict):
        w = tk.Toplevel(self)
        w.title(title)
        frm = ttk.Frame(w, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)
        for i, (k, v) in enumerate(metrics.items()):
            ttk.Label(frm, text=f"{k}:", width=20, anchor=tk.W).grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(frm, text=str(v)).grid(row=i, column=1, sticky=tk.W, pady=2)
        ttk.Button(frm, text="Close", command=w.destroy).grid(row=len(metrics), column=0, columnspan=2, pady=10)

    # --- Helpers ---
    def _create_swapped_problem(self):
        """Return a MazeProblem with S and G swapped (used by bidirectional search)."""
        matrix_2 = [row[:] for row in self.matrix]
        for r in range(len(matrix_2)):
            for c in range(len(matrix_2[0])):
                if matrix_2[r][c] == 'S':
                    matrix_2[r][c] = 'G'
                elif matrix_2[r][c] == 'G':
                    matrix_2[r][c] = 'S'
        mz_2 = Maze(matrix_2)
        return MazeProblem(mz_2)

    def _collect_tree_nodes(self, snapshots):
        """Helper to gather all reached nodes from snapshots for 'visited' effect."""
        nodes = set()
        for snap in snapshots:
            # Dijkstra/Greedy/A* format
            if snap.get('reached'):
                try:
                    nodes.update(tuple(state) for state in snap['reached'])
                except Exception: pass
            # Bidirectional format
            for key in ('reached_F', 'reached_B'):
                if key in snap:
                    try:
                        nodes.update(tuple(state) for state in snap[key])
                    except Exception: pass
        return nodes
    
    # --- Comparison and informed stubs ---
    def run_comparison_uninformed(self):
        # Run Dijkstra and Bidirectional multiple times and show averages
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output("Running comparison (15 runs each)...\n")

        def worker():
            import statistics
            d_times = []
            b_times = []
            d_nodes = []
            b_nodes = []
            d_found = 0
            b_found = 0
            for _ in range(15):
                try:
                    res_d, t_d, m_d, c_d, p_d = measure_time_memory(dijkstra, self.problem)
                except Exception:
                    continue
                if res_d is not None:
                    sol, ne = res_d
                    d_found += 1
                    d_times.append(t_d)
                    d_nodes.append(ne)

                def bid_call():
                    # create swapped problem fresh inside the thread
                    prob2 = self._create_swapped_problem()
                    return bidirectional_best_first_search(problem_F=self.problem, f_F=lambda n: n.g, problem_B=prob2, f_B=lambda n: n.g)

                try:
                    res_b, t_b, m_b, c_b, p_b = measure_time_memory(bid_call)
                except Exception:
                    continue
                if res_b is not None:
                    solb, neb = res_b
                    b_found += 1
                    b_times.append(t_b)
                    b_nodes.append(neb)

            metrics = {
                'Dijkstra avg time (ms)': f"{(statistics.mean(d_times) if d_times else 0):.3f}",
                'Dijkstra avg nodes': f"{(statistics.mean(d_nodes) if d_nodes else 0):.1f}",
                'Dijkstra found count': f"{d_found}/15",
                'Bidirectional avg time (ms)': f"{(statistics.mean(b_times) if b_times else 0):.3f}",
                'Bidirectional avg nodes': f"{(statistics.mean(b_nodes) if b_nodes else 0):.1f}",
                'Bidirectional found count': f"{b_found}/15",
            }
            # show_result_summary must run in main thread; schedule it
            from tkinter import Toplevel, ttk

            def show_table_comparison(title, metrics):
                win = Toplevel(self)
                win.title(title)
                win.geometry("500x200")

                # Adiciona uma coluna extra para as métricas
                tree = ttk.Treeview(win, columns=("Métrica", "Dijkstra", "Bidirectional"), show='headings')
                tree.heading("Métrica", text="Métrica")
                tree.heading("Dijkstra", text="Dijkstra")
                tree.heading("Bidirectional", text="Bidirectional")

                tree.column("Métrica", width=150, anchor='center')
                tree.column("Dijkstra", width=150, anchor='center')
                tree.column("Bidirectional", width=150, anchor='center')

                # Insere cada métrica como uma linha
                tree.insert("", "end", values=("Tempo médio (ms)",
                                            metrics['Dijkstra avg time (ms)'],
                                            metrics['Bidirectional avg time (ms)']))
                tree.insert("", "end", values=("Nós médios",
                                            metrics['Dijkstra avg nodes'],
                                            metrics['Bidirectional avg nodes']))
                tree.insert("", "end", values=("Encontrado",
                                            metrics['Dijkstra found count'],
                                            metrics['Bidirectional found count']))

                tree.pack(expand=True, fill='both', padx=10, pady=10)


            # Substitui a linha antiga:
            self.after(0, lambda: show_table_comparison('Comparação - Algoritmos Não Informados', metrics))



        self._run_in_thread(worker)

    def run_informed(self, algorithm: str, heuristic: str):
        # Delegate to dedicated per-algorithm runners for clarity and symmetry
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output(f"Running {algorithm} with {heuristic}...\n")

        if algorithm == 'A*':
            return self.run_a_star(heuristic)
        else:
            return self.run_greedy(heuristic)

    # --- Convenience wrappers for explicit informed runners ---
    def run_a_star(self, heuristic: str = 'manhattan'):
        """Run A* with measurement, re-run for snapshots, show metrics and animate.

        This method starts a background thread and mirrors the pattern used by
        the uninformed runners (measure first, then re-run to collect snapshots).
        """
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            try:
                from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
                choice = heuristic or 'manhattan'
                h_fn = h_manhattan_distance if choice == 'manhattan' else h_euclidean_distance if choice == 'euclidean' else h_octile_distance if choice == 'octile' else h_chebyshev_distance

                try:
                    from informed.a_star_search import a_star_search
                except Exception:
                    self.safe_write_output("A* not implemented in repository.\n")
                    return

                # Measure without callbacks to get timings/metrics
                def run_call_measure():
                    return a_star_search(self.problem, h_fn)

                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call_measure)
                if result is None:
                    self.after(0, lambda: self.show_result_summary(f"A* result", {'Status':'No path found'}))
                    return
                goal, nodes_expanded = result
                path = reconstruct_path(goal) if goal else None

                # Re-run to collect snapshots for GUI animation
                snapshots = []

                def on_step(snapshot):
                    try:
                        framesnap = {
                            'reached_F': [tuple(s) for s in snapshot.get('reached', [])],
                            'reached_B': [],
                            'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])],
                            'frontier_B': [],
                            'current': tuple(snapshot['current']) if snapshot.get('current') else None
                        }
                        snapshots.append(framesnap)
                    except Exception:
                        snapshots.append({'reached_F': [], 'reached_B': [], 'frontier_F': [], 'frontier_B': [], 'current': None})

                try:
                    _ = a_star_search(self.problem, h_fn, on_step=on_step)
                except Exception:
                    # If snapshot collection fails, continue to show metrics
                    pass

                self.safe_write_output(f"Path: {len(path) if path else 0,}\nNodes expanded: {nodes_expanded}\nCost: {getattr(goal, 'g', 'N/A')}\nTime: {elapsed_time:.3f} ms\nMemory used: {memory_used:.12f} B\n\n")
                metrics = {
                    'Status': 'Path found' if goal else 'No path',
                    'Path length': len(path) if path else 0,
                    'Cost': getattr(goal, 'g', 'N/A'),
                    'Nodes expanded': nodes_expanded,
                    'Time (ms)': f"{elapsed_time:.3f}",
                    'Memory (B)': f"{memory_used:.3f}",
                }
                self.after(0, lambda: self.show_result_summary(f"A* - {choice}", metrics))

                # Animate if snapshots were collected during the re-run
                try:
                    frames = len(snapshots) or 1
                    mult = float(self.default_playback_multiplier)
                    if self.default_visualize_use_runtime:
                        interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                    else:
                        interval_ms = int(self.default_frame_interval_ms)

                    if snapshots:
                        self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                        self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    # don't let animation issues hide metrics
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error running A*: {e}\n")

        self._run_in_thread(worker)

    def run_greedy(self, heuristic: str = 'manhattan'):
        """Run Greedy Best-First with measurement, re-run for snapshots, show metrics and animate."""
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            try:
                from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
                choice = heuristic or 'manhattan'
                heuristic_fn = h_manhattan_distance if choice == 'manhattan' else h_euclidean_distance if choice == 'euclidean' else h_octile_distance if choice == 'octile' else h_chebyshev_distance

                try:
                    from informed.greedy_best_first_search import greedy_best_first_search
                except Exception:
                    self.safe_write_output("Greedy not implemented in repository.\n")
                    return

                # Build heuristic table for greedy function
                heuristic_table_coordinate = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=heuristic_fn)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }

                # Measure without callback
                def run_call_measure():
                    return greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_coordinate)

                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call_measure)
                if result is None:
                    self.after(0, lambda: self.show_result_summary(f"Greedy result", {'Status':'No path found'}))
                    return
                goal, nodes_expanded = result
                path = reconstruct_path(goal) if goal else None

                # Re-run to collect snapshots
                snapshots = []

                def on_step(snapshot):
                    try:
                        framesnap = {
                            'reached_F': [tuple(s) for s in snapshot.get('reached', [])],
                            'reached_B': [],
                            'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])],
                            'frontier_B': [],
                            'current': tuple(snapshot['current']) if snapshot.get('current') else None
                        }
                        snapshots.append(framesnap)
                    except Exception:
                        snapshots.append({'reached_F': [], 'reached_B': [], 'frontier_F': [], 'frontier_B': [], 'current': None})

                try:
                    _ = greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_coordinate, on_step=on_step)
                except Exception:
                    pass
                
                self.safe_write_output(f"Path: {len(path) if path else 0,}\nNodes expanded: {nodes_expanded}\nCost: {getattr(goal, 'g', 'N/A')}\nTime: {elapsed_time:.3f} ms\nMemory used: {memory_used:.12f} B\n\n")
                metrics = {
                    'Status': 'Path found' if goal else 'No path',
                    'Path length': len(path) if path else 0,
                    'Cost': getattr(goal, 'g', 'N/A'),
                    'Nodes expanded': nodes_expanded,
                    'Time (ms)': f"{elapsed_time:.3f}",
                    'Memory (B)': f"{memory_used:.3f}",
                }
                self.after(0, lambda: self.show_result_summary(f"Greedy - {choice}", metrics))

                # Animate if snapshots were collected during the re-run
                try:
                    frames = len(snapshots) or 1
                    mult = float(self.default_playback_multiplier)
                    if self.default_visualize_use_runtime:
                        interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                    else:
                        interval_ms = int(self.default_frame_interval_ms)

                    if snapshots:
                        self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                        self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error running Greedy: {e}\n")

        self._run_in_thread(worker)

    def run_uninformed(self, algorithm: str = 'dijkstra'):
        """Wrapper to run an uninformed algorithm by name.

        algorithm: 'dijkstra' or 'bidirectional' (case-insensitive)
        """
        name = algorithm.lower() if isinstance(algorithm, str) else ''
        if name.startswith('d'):
            return self.run_dijkstra()
        if name.startswith('b'):
            return self.run_bidirectional()
        # unknown algorithm -> log and noop
        self.safe_write_output(f"Unknown uninformed algorithm: {algorithm}\n")
        return None

    def run_comparison_informed(self):
        # Run 8 informed variants (A*-Manhattan, A*-Euclidean, A*-Octile, A*-Chebyshev, Greedy-Manhattan, Greedy-Euclidean, Greedy-Octile, Greedy-Chebyshev)
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        self.safe_write_output("Running informed comparison (15 runs each if available)...\n")

        def worker():
            import statistics
            N = 15
            # Prepare containers
            times = {
                'A*-Manhattan': [],
                'A*-Euclidean': [],
                'A*-Octile': [],
                'A*-Chebyshev': [],
                'Greedy-Manhattan': [],
                'Greedy-Euclidean': [],
                'Greedy-Octile': [],
                'Greedy-Chebyshev': [],
            }
            nodes = {k: [] for k in times}
            found = {k: 0 for k in times}

            # Pre-build greedy heuristic tables
            from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
            try:
                from informed.a_star_search import a_star_search
            except Exception:
                a_star_search = None
            try:
                from informed.greedy_best_first_search import greedy_best_first_search
            except Exception:
                greedy_best_first_search = None

            heuristic_table_manh = None
            heuristic_table_euc = None
            if greedy_best_first_search is not None:
                heuristic_table_manh = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=h_manhattan_distance)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }
                heuristic_table_euc = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=h_euclidean_distance)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }
                heuristic_table_oct = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=h_octile_distance)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }
                heuristic_table_cheb = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=h_chebyshev_distance)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }

            for _ in range(N):
                # A* Manhattan
                if a_star_search is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(a_star_search, self.problem, h_manhattan_distance)
                        if res is not None:
                            sol, ne = res
                            found['A*-Manhattan'] += 1
                            times['A*-Manhattan'].append(t)
                            nodes['A*-Manhattan'].append(ne)
                    except Exception:
                        pass

                # A* Euclidean
                if a_star_search is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(a_star_search, self.problem, h_euclidean_distance)
                        if res is not None:
                            sol, ne = res
                            found['A*-Euclidean'] += 1
                            times['A*-Euclidean'].append(t)
                            nodes['A*-Euclidean'].append(ne)
                    except Exception:
                        pass

                # A* Octile
                if a_star_search is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(a_star_search, self.problem, h_octile_distance)
                        if res is not None:
                            sol, ne = res
                            found['A*-Octile'] += 1
                            times['A*-Octile'].append(t)
                            nodes['A*-Octile'].append(ne)
                    except Exception:
                        pass

                # A* Chebyshev
                if a_star_search is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(a_star_search, self.problem, h_chebyshev_distance)
                        if res is not None:
                            sol, ne = res
                            found['A*-Chebyshev'] += 1
                            times['A*-Chebyshev'].append(t)
                            nodes['A*-Chebyshev'].append(ne)
                    except Exception:
                        pass

                # Greedy Manhattan
                if greedy_best_first_search is not None and heuristic_table_manh is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(lambda: greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_manh))
                        if res is not None:
                            sol, ne = res
                            found['Greedy-Manhattan'] += 1
                            times['Greedy-Manhattan'].append(t)
                            nodes['Greedy-Manhattan'].append(ne)
                    except Exception:
                        pass

                # Greedy Euclidean
                if greedy_best_first_search is not None and heuristic_table_euc is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(lambda: greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_euc))
                        if res is not None:
                            sol, ne = res
                            found['Greedy-Euclidean'] += 1
                            times['Greedy-Euclidean'].append(t)
                            nodes['Greedy-Euclidean'].append(ne)
                    except Exception:
                        pass
                
                # Greedy Octile
                if greedy_best_first_search is not None and heuristic_table_oct is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(lambda: greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_oct))
                        if res is not None:
                            sol, ne = res
                            found['Greedy-Octile'] += 1
                            times['Greedy-Octile'].append(t)
                            nodes['Greedy-Octile'].append(ne)
                    except Exception:
                        pass

                # Greedy Chebyshev
                if greedy_best_first_search is not None and heuristic_table_cheb is not None:
                    try:
                        res, t, m, ccur, peak = measure_time_memory(lambda: greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_cheb))
                        if res is not None:
                            sol, ne = res
                            found['Greedy-Chebyshev'] += 1
                            times['Greedy-Chebyshev'].append(t)
                            nodes['Greedy-Chebyshev'].append(ne)
                    except Exception:
                        pass

            # Build metrics summary
            metrics = {
                'Avg time (ms)': {
                    k: f"{(statistics.mean(times[k]) if times[k] else 0):.3f}" for k in times
                },
                'Avg nodes': {
                    k: f"{(statistics.mean(nodes[k]) if nodes[k] else 0):.1f}" for k in nodes
                },
                'Found count': {k: f"{found[k]}/{N}" for k in found},
            }

            # schedule UI table creation in main thread
            from tkinter import Toplevel, ttk

            def show_table_comparison(title, metrics):
                win = Toplevel(self)
                win.title(title)
                win.geometry("700x220")

                cols = ("Métrica", "A*-Manhattan", "A*-Euclidean", "A*-Octile", "A*-Chebyshev", "Greedy-Manhattan", "Greedy-Euclidean", "Greedy-Octile", "Greedy-Chebyshev")
                tree = ttk.Treeview(win, columns=cols, show='headings')

                for col in cols:
                    tree.heading(col, text=col)

                # Define a largura de cada coluna (em pixels)
                tree.column("Métrica", width=130, anchor='center')
                tree.column("A*-Manhattan", width=120, anchor='center')
                tree.column("A*-Euclidean", width=120, anchor='center')
                tree.column("A*-Octile", width=120, anchor='center')
                tree.column("A*-Chebyshev", width=130, anchor='center')
                tree.column("Greedy-Manhattan", width=140, anchor='center')
                tree.column("Greedy-Euclidean", width=140, anchor='center')
                tree.column("Greedy-Octile", width=140, anchor='center')
                tree.column("Greedy-Chebyshev", width=140, anchor='center')

                tree.pack(expand=True, fill='both', padx=10, pady=10)

                # Inserindo as linhas
                tree.insert("", "end", values=("Avg time (ms)", metrics['Avg time (ms)']['A*-Manhattan'], metrics['Avg time (ms)']['A*-Euclidean'], metrics['Avg time (ms)']['A*-Octile'], metrics['Avg time (ms)']['A*-Chebyshev'], metrics['Avg time (ms)']['Greedy-Manhattan'], metrics['Avg time (ms)']['Greedy-Euclidean'], metrics['Avg time (ms)']['Greedy-Octile'], metrics['Avg time (ms)']['Greedy-Chebyshev']))
                tree.insert("", "end", values=("Avg nodes", metrics['Avg nodes']['A*-Manhattan'], metrics['Avg nodes']['A*-Euclidean'], metrics['Avg nodes']['A*-Octile'], metrics['Avg nodes']['A*-Chebyshev'], metrics['Avg nodes']['Greedy-Manhattan'], metrics['Avg nodes']['Greedy-Euclidean'], metrics['Avg nodes']['Greedy-Octile'], metrics['Avg nodes']['Greedy-Chebyshev']))
                tree.insert("", "end", values=("Found count", metrics['Found count']['A*-Manhattan'], metrics['Found count']['A*-Euclidean'], metrics['Found count']['A*-Octile'], metrics['Found count']['A*-Chebyshev'], metrics['Found count']['Greedy-Manhattan'], metrics['Found count']['Greedy-Euclidean'], metrics['Found count']['Greedy-Octile'], metrics['Found count']['Greedy-Chebyshev']))

            self.after(0, lambda: show_table_comparison('Informed Comparison', metrics))


        self._run_in_thread(worker)

    def run_heuristics_comparison(self):
        # Quick comparison of Manhattan vs Euclidean vs Octile vs Chebyshev for A* if available
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        if not self.has_a_star:
            messagebox.showinfo("Not available", "A* implementation not present; heuristics comparison skipped")
            return
        self.safe_write_output("Running heuristics comparison for A* (5 runs each)...\n")

        def worker():
            import statistics
            from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
            try:
                from informed.a_star_search import a_star_search
            except Exception:
                self.safe_write_output("A* not implemented in repository.\n")
                return
            man_times = []
            euc_times = []
            for _ in range(5):
                try:
                    res_m, t_m, *_ = measure_time_memory(a_star_search, self.problem, h_manhattan_distance)
                    if res_m is not None:
                        man_times.append(t_m)
                except Exception:
                    pass
                try:
                    res_e, t_e, *_ = measure_time_memory(a_star_search, self.problem, h_euclidean_distance)
                    if res_e is not None:
                        euc_times.append(t_e)
                except Exception:
                    pass
                try:
                    res_o, t_o, *_ = measure_time_memory(a_star_search, self.problem, h_octile_distance)
                except Exception:
                    pass
                try:
                    res_c, t_c, *_ = measure_time_memory(a_star_search, self.problem, h_chebyshev_distance)
                except Exception:
                    pass
            metrics = {
                'Manhattan avg time (ms)': f"{(statistics.mean(man_times) if man_times else 0):.3f}",
                'Euclidean avg time (ms)': f"{(statistics.mean(euc_times) if euc_times else 0):.3f}",
                'Octile avg time (ms)': f"{(statistics.mean(oct_times) if oct_times else 0):.3f}",
                'Chebyshev avg time (ms)': f"{(statistics.mean(che_times) if che_times else 0):.3f}",
            }
            self.after(0, lambda: self.show_result_summary('Heuristics Comparison (A*)', metrics))

        self._run_in_thread(worker)

    def browse_file(self):
        p = filedialog.askopenfilename(initialdir=os.path.dirname(self.default_maze_path), filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if p:
            self.path_var.set(p)

    def load_maze(self, path):
        try:
            matrix = read_matrix_from_file(path)
            self.matrix = matrix
            self.maze = Maze(matrix)
            self.problem = MazeProblem(self.maze)
            self.path_var.set(path)
            self.safe_write_output(f"Maze loaded from {path}\nStart: {self.maze.start} - Goal: {self.maze.goal}\nValid actions from start: {self.maze.actions(self.maze.start)}\n")
            # draw initial maze
            self.safe_draw_maze()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maze: {e}")

    def write_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def draw_maze(self, final_path=None, tree_nodes=None, visited=None):
        """Draw the current maze on the canvas.

        final_path is an iterable of (r,c).
        visited is an iterable of (r,c) that should be colored brown (visited cells).
        tree_nodes is an iterable of (r,c) to mark as tree expansion.
        """
        self.canvas.delete('all')
        if not self.matrix:
            return
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        pad = 2
        # compute cell size to fit canvas
        cw = max(4, int((self.canvas.winfo_width() - pad * 2) / max(cols, 1)))
        ch = max(4, int((self.canvas.winfo_height() - pad * 2) / max(rows, 1)))
        size = min(cw, ch)

        color_map = {
            '#': 'black',
            ' ': 'white',
            'S': 'green',
            'G': 'red',
        }

        path_set = set(final_path) if final_path else set()
        tree_set = set(tree_nodes) if tree_nodes else set()
        visited_set = set()
        if visited:
            try:
                visited_set = set(tuple(v) for v in (visited or []))
            except Exception:
                # fallback if already set-like
                try:
                    visited_set = set(visited)
                except Exception:
                    visited_set = set()

        for r in range(rows):
            for c in range(cols):
                chv = self.matrix[r][c]
                x0 = pad + c * size
                y0 = pad + r * size
                x1 = x0 + size
                y1 = y0 + size
                fill = color_map.get(chv, 'white')
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline='gray')
                # draw visited cells (brown) if present and not special cells
                if (r, c) in visited_set and chv not in ('S', 'G', '#'):
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill='#8c564b', outline='')
                if (r, c) in tree_set and chv not in ('S', 'G', '#'):
                    # draw search tree marker
                    self.canvas.create_oval(x0 + size*0.3, y0 + size*0.3, x1 - size*0.3, y1 - size*0.3, outline='sienna', width=1)
        # draw final path as overlay
        if final_path:
            for (r, c) in final_path:
                x0 = pad + c * size
                y0 = pad + r * size
                x1 = x0 + size
                y1 = y0 + size
                # path cell
                self.canvas.create_rectangle(x0, y0, x1, y1, fill='lime', outline='lime')
        # keep reference to last drawn
        self._last_drawn = {
            'path': list(final_path) if final_path else None,
            'tree': list(tree_nodes) if tree_nodes else None,
            'visited': list(visited_set) if visited_set else None,
        }

    def _run_in_thread(self, target, args=()):
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()

    def animate_snapshots(self, snapshots, interval_ms: int = 100, final_path=None):
        """Animate a list of snapshots with a legend and consistent colors."""
        if not snapshots:
            self.safe_draw_maze(final_path=final_path)
            return
        
        PALETTE = [
            '#000000',  # 0 wall
            '#ffffff',  # 1 free cell
            '#2ca02c',  # 2 start
            '#d62728',  # 3 goal
            '#1f77b4',  # 4 reached forward (blue)
            '#ff00ff',  # 5 reached backward (magenta)
            '#ff7f0e',  # 6 frontier forward (orange)
            '#17becf',  # 7 frontier backward (cyan)
            '#ffe680',  # 8 current node (yellow)
            '#32cd32',  # 9 final path (lime green)
            '#8c564b',  # 10 search tree (brown)
        ]

        # Precompute frames
        frames = []
        for snap in snapshots:
            reached_f, reached_b = set(), set()
            frontier_f, frontier_b = set(), set()
            current = None

            for s in snap.get('reached_F', []):
                try: reached_f.add(tuple(s))
                except Exception: pass
            for s in snap.get('reached_B', []):
                try: reached_b.add(tuple(s))
                except Exception: pass
            for s in snap.get('frontier_F', []):
                try: frontier_f.add(tuple(s))
                except Exception: pass
            for s in snap.get('frontier_B', []):
                try: frontier_b.add(tuple(s))
                except Exception: pass
            cur = snap.get('current')
            if cur:
                try: current = tuple(cur)
                except Exception: current = None

            frames.append({
                'reached_F': reached_f,
                'reached_B': reached_b,
                'frontier_F': frontier_f,
                'frontier_B': frontier_b,
                'current': current,
                'tree': set()
            })

        # compute union of all reached cells across frames -> these are 'visited' for final draw
        visited_all = set()
        for fr in frames:
            try:
                visited_all |= set(fr.get('reached_F', set()))
                visited_all |= set(fr.get('reached_B', set()))
            except Exception:
                pass

        # Draw legend function
        def draw_legend():
            legend_items = [
                ('Wall', 0),
                ('Free', 1),
                ('Start', 2),
                ('Goal', 3),
                ('Reached F', 4),
                ('Reached B', 5),
                ('Frontier F', 6),
                ('Frontier B', 7),
                ('Current', 8),
                ('Final Path', 9),
                ('Search Tree', 10),
            ]
            # posição da legenda no lado direito
            canvas_width = int(self.canvas['width'])
            x0 = canvas_width - 100  # ajustar largura do legend box
            y0 = 10
            for i, (name, idx) in enumerate(legend_items):
                y = y0 + i*20
                self.canvas.create_rectangle(x0, y, x0+15, y+15, fill=PALETTE[idx])
                self.canvas.create_text(x0+20, y+7, anchor='w', text=name, font=('Arial', 10), fill='white')



        # make animation cancelable via stop_animation
        # cancel any previous animation
        try:
            if getattr(self, '_anim_after_id', None):
                try:
                    self.after_cancel(self._anim_after_id)
                except Exception:
                    pass
                self._anim_after_id = None
        except Exception:
            pass

        self._animating = True

        # schedule drawing frames on the Tkinter mainloop
        def play(idx=0):
            # stop if requested
            if not getattr(self, '_animating', True):
                self._anim_after_id = None
                return

            if idx >= len(frames):
                try:
                    # final draw: include visited cells as brown
                    self.draw_maze(final_path=final_path, tree_nodes=set(), visited=visited_all)
                    draw_legend()
                except Exception:
                    pass
                self._animating = False
                self._anim_after_id = None
                return

            f = frames[idx]
            try:
                self.draw_maze(final_path=None, tree_nodes=f.get('tree'))

                for r, c in f.get('reached_F', set()):
                    self._draw_cell_overlay(r, c, fill=PALETTE[4])
                for r, c in f.get('reached_B', set()):
                    self._draw_cell_overlay(r, c, fill=PALETTE[5])
                for r, c in f.get('frontier_F', set()):
                    self._draw_cell_overlay(r, c, fill=PALETTE[6])
                for r, c in f.get('frontier_B', set()):
                    self._draw_cell_overlay(r, c, fill=PALETTE[7])
                if f.get('current'):
                    r, c = f['current']
                    self._draw_cell_overlay(r, c, fill=PALETTE[8])

                draw_legend()
            except Exception:
                pass

            # schedule next frame and keep track of the after id so it can be canceled
            try:
                self._anim_after_id = self.after(max(1, int(interval_ms)), lambda: play(idx + 1))
            except Exception:
                # if scheduling fails, stop animation
                self._animating = False
                self._anim_after_id = None

        # start
        play(0)

    def _draw_cell_overlay(self, r, c, fill='#add8e6'):
        """Draw a colored rectangle over a given cell coordinate (r,c) without clearing canvas."""
        if not self.matrix:
            return
        rows = len(self.matrix)
        cols = len(self.matrix[0])
        pad = 2
        cw = max(4, int((self.canvas.winfo_width() - pad * 2) / max(cols, 1)))
        ch = max(4, int((self.canvas.winfo_height() - pad * 2) / max(rows, 1)))
        size = min(cw, ch)
        x0 = pad + c * size
        y0 = pad + r * size
        x1 = x0 + size
        y1 = y0 + size
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline='')

    # --- Main algorithm runners (now use default visualization without asking) ---
    def run_dijkstra(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Running Dijkstra...\n")
            snapshots = []

            # 1) Medir o algoritmo puro (sem on_step) para métricas "reais"
            try:
                result, elapsed_time, memory_used, current, peak = measure_time_memory(dijkstra, self.problem, None)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                goal_node, nodes_expanded = result
                path = reconstruct_path(goal_node) if goal_node else None
            except Exception as e:
                self.safe_write_output(f"Error running Dijkstra (measurement): {e}\n")
                return

            # 2) Agora (opcional) reexecuta a busca para coletar snapshots para visualização.
            #    Isso não altera as métricas já medidas.
            def on_step_collect(snapshot):
                # normalize snapshot to GUI format
                snap_copy = {
                    'reached_F': [tuple(n) for n in snapshot.get('reached', [])],
                    'reached_B': [],
                    'frontier_F': [tuple(n) for n in snapshot.get('frontier', [])],
                    'frontier_B': [],
                    'current': tuple(snapshot['current']) if snapshot.get('current') else None
                }
                snapshots.append(snap_copy)

            try:
                # run *without* measuring, only to gather snapshots for animation
                _ = dijkstra(self.problem, on_step=on_step_collect)
            except Exception:
                # if collecting snapshots fails, we still show the measured result
                pass

            # Compute animation interval based on measured elapsed_time (pure algorithm time)
            frames = len(snapshots) or 1
            mult = float(self.default_playback_multiplier)
            if self.default_visualize_use_runtime:
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
            else:
                interval_ms = int(self.default_frame_interval_ms)

            try:
                # schedule animation in main thread using collected snapshots
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
            except Exception as e:
                self.safe_write_output(f"Animation failed: {e}\n")

            # show measured metrics (these are the "reais") and open summary window
            self.safe_write_output(f"Path: {path}\nNodes expanded: {nodes_expanded}\nCost: {goal_node.g if goal_node else 'N/A'}\nTime: {elapsed_time:.3f} ms\nMemory used: {memory_used:.12f} B\n\n")
            metrics = {
                'Status': 'Path found' if goal_node else 'No path',
                'Path length': len(path) if path else 0,
                'Cost': getattr(goal_node, 'g', 'N/A'),
                'Nodes expanded': nodes_expanded,
                'Time (ms)': f"{elapsed_time:.3f}",
                'Memory (B)': f"{memory_used:.3f}",
            }
            self.after(0, lambda: self.show_result_summary('Dijkstra - result', metrics))

        self._run_in_thread(worker)

    def run_bidirectional(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Running Bidirectional Best-First Search...\n")
            snapshots = []

            # Prepare backward problem (no snapshots)
            problem_2 = self._create_swapped_problem()

            # 1) Medir o algoritmo sem callback (tempo "real")
            def run_call_no_cb():
                return bidirectional_best_first_search(problem_F=self.problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g)

            try:
                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call_no_cb)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None
            except Exception as e:
                self.safe_write_output(f"Error running Bidirectional (measurement): {e}\n")
                return

            # 2) Re-executar apenas para coletar snapshots (não medido)
            def on_step_collect(snapshot):
                try:
                    snapshots.append(snapshot.copy())
                except Exception:
                    snapshots.append(dict(snapshot))

            try:
                # run without measuring to get snapshots for visualization
                _ = bidirectional_best_first_search(problem_F=self.problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g, on_step=on_step_collect)
            except Exception:
                pass

            # compute interval based on measured elapsed_time
            frames = len(snapshots) or 1
            mult = float(self.default_playback_multiplier)
            if self.default_visualize_use_runtime:
                interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
            else:
                interval_ms = int(self.default_frame_interval_ms)

            try:
                self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
            except Exception as e:
                self.safe_write_output(f"Animation failed: {e}\n")

            # show measured metrics and open summary window (match Informed behavior)
            self.safe_write_output(f"Path: {path}\nNodes expanded: {nodes_expanded}\nCost: {solution.g if solution else 'N/A'}\nTime: {elapsed_time:.3f} ms\nMemory used: {memory_used:.12f} B\n\n")
            metrics = {
                'Status': 'Path found' if solution else 'No path',
                'Path length': len(path) if path else 0,
                'Cost': getattr(solution, 'g', 'N/A'),
                'Nodes expanded': nodes_expanded,
                'Time (ms)': f"{elapsed_time:.3f}",
                'Memory (B)': f"{memory_used:.3f}",
            }
            self.after(0, lambda: self.show_result_summary('Bidirectional - result', metrics))


        self._run_in_thread(worker)

    def visualize_dijkstra(self):
        # Esta função agora normaliza os snapshots, corrigindo a animação em branco.
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Visualizing Dijkstra (this may take a while)...\n")
            snapshots = []

            # --- INÍCIO DA CORREÇÃO ---
            # O on_step agora normaliza o snapshot para o formato que
            # a função 'animate_snapshots' espera (igual ao 'run_dijkstra')
            def on_step(snapshot):
                try:
                    snap_copy = {
                        'reached_F': [tuple(n) for n in snapshot.get('reached', [])],
                        'reached_B': [],
                        'frontier_F': [tuple(n) for n in snapshot.get('frontier', [])],
                        'frontier_B': [],
                        'current': tuple(snapshot['current']) if snapshot.get('current') else None
                    }
                    snapshots.append(snap_copy)
                except Exception:
                    # Fallback em caso de erro na normalização
                    snapshots.append({'reached_F': [], 'reached_B': [], 'frontier_F': [], 'frontier_B': [], 'current': None})
            # --- FIM DA CORREÇÃO ---

            try:
                # Measure execution time while running dijkstra with snapshots
                result, elapsed_time, memory_used, current, peak = measure_time_memory(dijkstra, self.problem, on_step=on_step)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None

                # Animate if we collected snapshots
                try:
                    frames = len(snapshots) or 1
                    mult = float(self.default_playback_multiplier)
                    if self.default_visualize_use_runtime:
                        interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                    else:
                        interval_ms = int(self.default_frame_interval_ms)

                    if snapshots:
                        self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                        self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error visualizing Dijkstra: {e}\n")

        self._run_in_thread(worker)

    def visualize_bidirectional(self):
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            self.safe_write_output("Visualizing Bidirectional (this may take a while)...\n")
            snapshots = []

            def on_step(snapshot):
                snapshots.append(snapshot.copy())

            try:
                # Prepare backward problem by swapping S and G
                problem_2 = self._create_swapped_problem()

                # Run and collect snapshots
                def run_call():
                    return bidirectional_best_first_search(problem_F=self.problem, f_F=lambda n: n.g, problem_B=problem_2, f_B=lambda n: n.g, on_step=on_step)

                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None

                frames = len(snapshots) or 1
                mult = float(self.default_playback_multiplier)
                if self.default_visualize_use_runtime:
                    interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                else:
                    interval_ms = int(self.default_frame_interval_ms)

                try:
                    self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                    self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error visualizing Bidirectional: {e}\n")

        self._run_in_thread(worker)

    def open_visualize_informed_window(self):
        w = tk.Toplevel(self)
        w.title("Visualize Informed")
        ttk.Label(w, text="Choose visualization (Informed):").pack(padx=10, pady=8)
        # Heuristic selector
        ttk.Label(w, text="Choose heuristic:").pack(padx=10, pady=(6, 2))
        heur_frame = ttk.Frame(w)
        heur_frame.pack(padx=10, pady=(0, 6))
        ttk.Radiobutton(heur_frame, text="Manhattan", variable=self._viz_informed_heur_var, value='manhattan').pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(heur_frame, text="Euclidean", variable=self._viz_informed_heur_var, value='euclidean').pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(heur_frame, text="Octile", variable=self._viz_informed_heur_var, value='octile').pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(heur_frame, text="Chebyshev", variable=self._viz_informed_heur_var, value='chebyshev').pack(side=tk.LEFT, padx=4)
        a_star_state = ' (missing)' if not self.has_a_star else ''
        greedy_state = ' (missing)' if not self.has_greedy else ''
        ttk.Button(w, text=f"Visualize A*{a_star_state}", command=lambda: [w.destroy(), self.visualize_a_star()]).pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(w, text=f"Visualize Greedy{greedy_state}", command=lambda: [w.destroy(), self.visualize_greedy()]).pack(fill=tk.X, padx=8, pady=4)
    # Note: Save-as-GIF actions were removed; GIFs are auto-saved when the
    # user clicked 'Visualize Informed Searches'. The window only offers
    # in-canvas visualizations now.
        ttk.Button(w, text="Back", command=w.destroy).pack(fill=tk.X, padx=8, pady=6)

    def visualize_a_star(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        if not self.has_a_star:
            messagebox.showinfo("Not available", "A* implementation not present; visualization skipped")
            return

        def worker():
            self.safe_write_output("Visualizing A* (this may take a while)...\n")
            snapshots = []

            def on_step(snapshot):
                try:
                    framesnap = {
                        'reached_F': [tuple(s) for s in snapshot.get('reached', [])],
                        'reached_B': [],
                        'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])],
                        'frontier_B': [],
                        'current': tuple(snapshot['current']) if snapshot.get('current') else None
                    }
                    snapshots.append(framesnap)
                except Exception:
                    snapshots.append({'reached_F': [], 'reached_B': [], 'frontier_F': [], 'frontier_B': [], 'current': None})

            try:
                # pick heuristic based on UI selection
                from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
                try:
                    from informed.a_star_search import a_star_search
                except Exception:
                    self.safe_write_output("A* import failed.\n")
                    return
                choice = self._viz_informed_heur_var.get() if hasattr(self, '_viz_informed_heur_var') else 'manhattan'
                h_fn = h_manhattan_distance if choice == 'manhattan' else h_euclidean_distance if choice == 'euclidean' else h_octile_distance if choice == 'octile' else h_chebyshev_distance

                def run_call():
                    return a_star_search(self.problem, h_fn, on_step=on_step)

                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None

                frames = len(snapshots) or 1
                mult = float(self.default_playback_multiplier)
                if self.default_visualize_use_runtime:
                    interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                else:
                    interval_ms = int(self.default_frame_interval_ms)

                try:
                    self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                    self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error visualizing A*: {e}\n")

        self._run_in_thread(worker)

    def visualize_greedy(self):
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return
        if not self.has_greedy:
            messagebox.showinfo("Not available", "Greedy implementation not present; visualization skipped")
            return

        def worker():
            self.safe_write_output("Visualizing Greedy Best-First Search (this may take a while)...\n")
            snapshots = []

            def on_step(snapshot):
                try:
                    framesnap = {
                        'reached_F': [tuple(s) for s in snapshot.get('reached', [])],
                        'reached_B': [],
                        'frontier_F': [tuple(s) for s in snapshot.get('frontier', [])],
                        'frontier_B': [],
                        'current': tuple(snapshot['current']) if snapshot.get('current') else None
                    }
                    snapshots.append(framesnap)
                except Exception:
                    snapshots.append({'reached_F': [], 'reached_B': [], 'frontier_F': [], 'frontier_B': [], 'current': None})

            try:
                from core.heuristics import h_manhattan_distance, h_euclidean_distance, h_octile_distance, h_chebyshev_distance
                try:
                    from informed.greedy_best_first_search import greedy_best_first_search
                except Exception:
                    self.safe_write_output("Greedy import failed.\n")
                    return

                # build heuristic table like the module expects according to UI selection
                choice = self._viz_informed_heur_var.get() if hasattr(self, '_viz_informed_heur_var') else 'manhattan'
                heuristic_fn = h_manhattan_distance if choice == 'manhattan' else h_euclidean_distance if choice == 'euclidean' else h_octile_distance if choice == 'octile' else h_chebyshev_distance

                heuristic_table_coordinate = {
                    (r, c): self.problem.heuristic((r, c), self.problem.goal, function_h=heuristic_fn)
                    for r in range(self.problem.maze.H) for c in range(self.problem.maze.W)
                }

                def run_call():
                    return greedy_best_first_search(self.problem, lambda n: n.h, heuristic_table_coordinate, on_step=on_step)

                result, elapsed_time, memory_used, current, peak = measure_time_memory(run_call)
                if result is None:
                    self.safe_write_output("No path found\n")
                    return
                solution, nodes_expanded = result
                path = reconstruct_path(solution) if solution else None

                frames = len(snapshots) or 1
                mult = float(self.default_playback_multiplier)
                if self.default_visualize_use_runtime:
                    interval_ms = max(self.default_frame_interval_ms, int((elapsed_time / frames) * mult))
                else:
                    interval_ms = int(self.default_frame_interval_ms)

                try:
                    self.safe_animate_snapshots(snapshots, interval_ms, final_path=path)
                    self.safe_write_output("Animation played in GUI.\n")
                except Exception as e:
                    self.safe_write_output(f"Animation failed: {e}\n")

            except Exception as e:
                self.safe_write_output(f"Error visualizing Greedy: {e}\n")

        self._run_in_thread(worker)

    def save_informed_gif(self, alg: str):
        """Run the informed GIF generator in background using the UI-selected heuristic.

        alg: 'a_star' or 'greedy'
        """
        if not self.problem:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        def worker():
            try:
                self.safe_write_output(f"Generating GIF for {alg} with heuristic={self._viz_informed_heur_var.get()}...\n")
                from informed.generate_gifs_informed import generate_gifs_informed
                # build an out_file under repo root data/visualizations
                repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                heur = self._viz_informed_heur_var.get() if hasattr(self, '_viz_informed_heur_var') else 'manhattan'
                out_name = f'visualization-{alg}-{heur}.gif'
                out_path = os.path.join(repo_root, out_name)

                res = generate_gifs_informed(self.problem, self.matrix, heuristic=heur, algorithm=('greedy' if alg=='greedy' else 'a_star'), interval_ms=100, out_file=out_path)
                if res:
                    self.safe_write_output(f"Saved GIF to: {res}\n")
                    messagebox.showinfo("Saved", f"Saved GIF to: {res}")
                else:
                    self.safe_write_output("Generator reported no output (no path or snapshots)\n")
                    messagebox.showinfo("No output", "No GIF was produced (no path or snapshots)")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                self.safe_write_output(f"Error generating GIF: {e}\n{tb}\n")

        self._run_in_thread(worker)

    def save_all_informed_gifs_and_open_visualizer(self):
        """Save 4 GIFs (A*/Greedy × Manhattan/Euclidean/Octile/Chebyshev) in background, then open the visualize window.

        This is called when the user clicks 'Visualize Informed Searches'. The
        method will schedule background work to generate the GIFs and will
        immediately open the visualize window so the user can choose canvas
        visualizations while the GIFs are being produced.
        """
        # Open visualize window immediately (non-blocking) so user can visualize
        # on canvas while GIFs are being generated.
        try:
            self.open_visualize_informed_window()
        except Exception:
            pass

        def worker():
            try:
                self.safe_write_output("Auto-saving informed GIFs (A*/Greedy × Manhattan/Euclidean/Octile/Chebyshev)...\n")
                from informed.generate_gifs_informed import generate_gifs_informed
                from pathlib import Path
                import os

                # Tenta obter repo_root a partir de __file__; se não existir (ex.: REPL), usa cwd
                try:
                    current_file = Path(__file__).resolve()
                    repo_root = current_file.parents[2]  # sobe dois níveis
                except Exception:
                    repo_root = Path.cwd()
                    self.safe_write_output(f"__file__ não disponível — usando cwd como repo_root: {repo_root}\n")

                # Se quiser forçar um comportamento alternativo, descomente e ajuste:
                # repo_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

                output_dir = repo_root / 'data' / 'output' / 'visualization' / 'informed'
                # Garante que o diretório exista
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.safe_write_output(f"Falha ao criar diretório {output_dir}: {e}\n")
                    raise

                self.safe_write_output(f"Usando repo_root = {repo_root}\n")
                self.safe_write_output(f"Output dir = {output_dir}\n")

                combos = [
                    ('a_star', 'manhattan'),
                    ('a_star', 'euclidean'),
                    ('a_star', 'octile'),
                    ('a_star', 'chebyshev'),
                    ('greedy', 'manhattan'),
                    ('greedy', 'euclidean'),
                    ('greedy', 'octile'),
                    ('greedy', 'chebyshev'),
                ]
                results = []
                for alg, heur in combos:
                    out_name = f'visualization-{alg}-{heur}.gif'
                    out_path = output_dir / out_name
                    try:
                        self.safe_write_output(f"Generating {alg} with {heur} -> {out_path} ...\n")
                        # Certifica-se de passar strings/paths conforme a função espera
                        res = generate_gifs_informed(
                            problem=self.problem,
                            matrix=self.matrix,
                            heuristic=heur,
                            algorithm=('greedy' if alg == 'greedy' else 'a_star'),
                            interval_ms=100,
                            out_file=str(out_path)  # converte para str caso a função não aceite Path
                        )
                        if res:
                            # se a função retorna o caminho, mostra; se salva direto, mostra out_path
                            saved = res if isinstance(res, str) else str(out_path)
                            self.safe_write_output(f"Saved: {saved}\n")
                            results.append((alg, heur, True, saved))
                        else:
                            # sem retorno explícito — verifica existência do arquivo
                            if out_path.exists():
                                self.safe_write_output(f"Arquivo criado: {out_path}\n")
                                results.append((alg, heur, True, str(out_path)))
                            else:
                                self.safe_write_output(f"No output for {alg} {heur}\n")
                                results.append((alg, heur, False, None))
                    except Exception as e:
                        import traceback
                        tb = traceback.format_exc()
                        self.safe_write_output(f"Error generating {alg} {heur}: {e}\n{tb}\n")
                        results.append((alg, heur, False, str(e)))

                # Summarize
                ok_count = sum(1 for r in results if r[2])
                self.safe_write_output(f"Auto-save complete: {ok_count}/{len(results)} GIFs saved.\n")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                self.safe_write_output(f"Error in auto-save worker: {e}\n{tb}\n")

        self._run_in_thread(worker)

    def save_all_uninformed_gifs_and_open_visualizer(self):
        """Save 2 GIFs (Dijkstra/Bidirectional) in background, then open the visualize window."""
        if not self.problem or not self.matrix:
            messagebox.showwarning("No maze", "Load a maze first")
            return

        # Open visualize window immediately (non-blocking) so user can visualize
        # on canvas while GIFs are being generated.
        try:
            self.open_visualize_uninformed_window()
        except Exception:
            pass

        def worker():
            try:
                self.safe_write_output("Auto-saving uninformed GIFs (Dijkstra/Bidirectional)...\n")
                # Importações necessárias para o worker
                from pathlib import Path
                import os
                import tempfile 

                # 1. Definir o diretório de saída (espelhando a lógica do 'informed')
                try:
                    current_file = Path(__file__).resolve()
                    repo_root = current_file.parents[2]  # sobe de src/tools/run_gui.py
                except Exception:
                    repo_root = Path.cwd()
                    self.safe_write_output(f"__file__ não disponível — usando cwd como repo_root: {repo_root}\n")
                
                output_dir = repo_root / 'data' / 'output' / 'visualization' / 'uninformed'
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.safe_write_output(f"Falha ao criar diretório {output_dir}: {e}\n")
                    raise

                self.safe_write_output(f"Output dir = {output_dir}\n")
                # Usar um intervalo padrão, já que não podemos usar input() no GUI
                default_interval_ms = 100
                
                # Criar um arquivo temporário com a matriz atual
                # Isto é mais seguro do que usar self.path_var.get(), pois garante
                # que o GIF corresponda à matriz em memória.
                tmp_maze_path = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tf:
                        tmp_maze_path = tf.name
                        for row in self.matrix:
                            tf.write(''.join(row) + '\n')
                    
                    if not tmp_maze_path:
                        raise Exception("Failed to create temp maze file")

                    # --- 2. Gerar GIF do Dijkstra ---
                    self.safe_write_output("Generating Dijkstra GIF...\n")
                    snapshots_d = []
                    def on_step_d(snapshot):
                        snapshots_d.append(snapshot.copy())
                    
                    try:
                        resultDijkstra = dijkstra(self.problem, on_step=on_step_d)
                        if resultDijkstra is None:
                            self.safe_write_output("Dijkstra: No path found, GIF skipped.\n")
                        else:
                            solution, nodes_expanded = resultDijkstra
                            out_path_d = output_dir / 'visualization-dijkstra.gif'
                            
                            # Chamar a função de visualização (já importada no topo do run_gui.py)
                            visualize_matrix.visualize(
                                tmp_maze_path, # Usar o path do arquivo temporário
                                f=lambda n: n.g,
                                interval=default_interval_ms,
                                precompute=True,
                                precomputed_snapshots=snapshots_d,
                                final_path=reconstruct_path(solution) if solution else None,
                                tree_nodes=self._collect_tree_nodes(snapshots_d),
                                final_hold_ms=5000,
                                out_file=str(out_path_d),
                            )
                            self.safe_write_output(f"Saved Dijkstra GIF to {out_path_d}\n")
                    except Exception as e:
                        self.safe_write_output(f"Error generating Dijkstra GIF: {e}\n")

                    # --- 3. Gerar GIF do Bidirectional ---
                    self.safe_write_output("Generating Bidirectional GIF...\n")
                    snapshots_b = []
                    def on_step_b(snapshot):
                        snapshots_b.append(snapshot.copy())
                    
                    try:
                        problem_2 = self._create_swapped_problem()
                        resultBid = bidirectional_best_first_search(
                            problem_F=self.problem, f_F=lambda n: n.g,
                            problem_B=problem_2, f_B=lambda n: n.g,
                            on_step=on_step_b
                        )
                        
                        if resultBid is None:
                            self.safe_write_output("Bidirectional: No path found, GIF skipped.\n")
                        else:
                            solution, nodes_expanded = resultBid
                            out_path_b = output_dir / 'visualization-bidirectional.gif'
                            
                            visualize_matrix.visualize(
                                tmp_maze_path, # Usar o path do arquivo temporário
                                f=lambda n: n.g,
                                interval=default_interval_ms,
                                precompute=True,
                                precomputed_snapshots=snapshots_b,
                                final_path=reconstruct_path(solution) if solution else None,
                                tree_nodes=self._collect_tree_nodes(snapshots_b),
                                final_hold_ms=5000,
                                out_file=str(out_path_b),
                            )
                            self.safe_write_output(f"Saved Bidirectional GIF to {out_path_b}\n")
                    except Exception as e:
                        self.safe_write_output(f"Error generating Bidirectional GIF: {e}\n")

                    self.safe_write_output("Auto-save complete for uninformed GIFs.\n")

                finally:
                    # Limpar o arquivo temporário
                    if tmp_maze_path and os.path.exists(tmp_maze_path):
                        try:
                            os.unlink(tmp_maze_path)
                        except Exception as e:
                            self.safe_write_output(f"Warning: could not delete temp file {tmp_maze_path}: {e}\n")

            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                self.safe_write_output(f"Error in uninformed auto-save worker: {e}\n{tb}\n")

        self._run_in_thread(worker)

if __name__ == '__main__':
    app = App()
    app.mainloop()
