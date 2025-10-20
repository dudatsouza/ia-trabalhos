# EXTERNAL IMPORTS
from __future__ import annotations
from typing import Callable, Dict, Any, List, Tuple, Iterable
import heapq
import os
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

# INTERNAL PROJECT IMPORTS
from core.maze_representation import Maze
from core.maze_generator import read_matrix_from_file
from core.maze_problem import MazeProblem
from core.node import Node

# GLOBAL VARIABLES
# FIXED PALETTE INDICES USED BY SNAPSHOT TO ARRAY AND GIF SAVER
PALETTE = [
    '#000000',  # WALL
    '#ffffff',  # FREE CELL
    '#2ca02c',  # START
    '#d62728',  # GOAL
    '#1f77b4',  # REACHED FORWARD
    '#ff00ff',  # REACHED BACKWARD
    '#ff7f0e',  # FRONTIER FORWARD
    '#17becf',  # FRONTIER BACKWARD
    '#ffe680',  # CURRENT NODE
    '#32cd32',  # FINAL PATH
    '#8c564b',  # SEARCH TREE
]

_LAST_ANIMATION: animation.FuncAnimation | None = None

# FUNCTION TO YIELD SNAPSHOTS DURING BEST-FIRST SEARCH
def best_first_search_steps(problem: MazeProblem, f: Callable[[Node], float]) -> Iterable[Dict[str, Any]]:
    # INITIALIZE START NODE AND FRONTIER
    start = Node(state=problem.initial, g=0.0, h=problem.heuristic(problem.initial))
    frontier: List[Tuple[float, Node]] = []
    heapq.heappush(frontier, (f(start), start))
    reached: Dict[Any, Node] = {start.state: start}
    nodes_expanded = 0

    # FUNCTION TO CREATE SNAPSHOT DICTIONARY
    def make_snapshot(current: Node | None, event: str) -> Dict[str, Any]:
        return {
            'current': current.state if current else None,
            'frontier': [(n.state, float(priority)) for priority, n in frontier],
            'reached': {s: node.g for s, node in reached.items()},
            'parents': {s: node.parent.state if node.parent else None for s, node in reached.items()},
            'nodes_expanded': nodes_expanded,
            'event': event,
        }

    # MAIN LOOP OF BEST-FIRST SEARCH
    while frontier:
        _, node = heapq.heappop(frontier)
        yield make_snapshot(node, 'pop')
        if problem.is_goal(node.state):
            yield make_snapshot(node, 'goal')
            return

        nodes_expanded += 1
        for action in problem.actions(node.state):
            successor = problem.result(node.state, action)
            cost = node.g + problem.action_cost(node.state, action, successor)
            child = Node(state=successor, parent=node, action=action, g=cost, h=problem.heuristic(successor))
            existing = reached.get(child.state)
            if existing is None or child.g < existing.g:
                reached[child.state] = child
                heapq.heappush(frontier, (f(child), child))
                yield make_snapshot(child, 'push')

    yield make_snapshot(None, 'finished')

# FUNCTION TO CONVERT SNAPSHOT TO NUMPY ARRAY FOR VISUALIZATION
def snapshot_to_array(snapshot: Dict[str, Any], base_grid: List[List[str]], allow_override_start_goal: bool = False) -> np.ndarray:
    height = len(base_grid)
    width = len(base_grid[0])
    arr = np.zeros((height, width), dtype=np.uint8)

    # MAP BASE GRID CHARACTERS TO PALETTE INDICES
    for r in range(height):
        for c in range(width):
            ch = base_grid[r][c]
            if ch == '#':
                arr[r, c] = 0
            elif ch == 'S':
                arr[r, c] = 2
            elif ch == 'G':
                arr[r, c] = 3
            else:
                arr[r, c] = 1

    # FUNCTION TO CHECK IF CELL CAN BE PAINTED
    def can_paint(row: int, col: int) -> bool:
        if not (isinstance(row, int) and isinstance(col, int)):
            return False
        if not (0 <= row < len(base_grid) and 0 <= col < len(base_grid[0])):
            return False
        if allow_override_start_goal:
            return True
        return base_grid[row][col] not in ('S', 'G')

    # FUNCTION TO CONVERT VARIOUS STATE FORMATS TO (ROW, COL)
    def _coerce_state(state) -> tuple | None:
        if isinstance(state, (list, tuple)) and len(state) == 2:
            a, b = state
            if isinstance(a, (list, tuple)) and len(a) >= 2 and isinstance(a[0], int):
                try:
                    return int(a[0]), int(a[1])
                except Exception:
                    return None
            if isinstance(a, int) and isinstance(b, int):
                return int(a), int(b)
        try:
            import numpy as _np
            if isinstance(state, _np.ndarray) and state.size >= 2:
                return int(state[0]), int(state[1])
        except Exception:
            pass
        if isinstance(state, (list, tuple)) and len(state) >= 2:
            r, c = state[0], state[1]
            if isinstance(r, int) and isinstance(c, int):
                return r, c
        return None

    # MARK REACHED NODES
    if 'reached' in snapshot and snapshot['reached']:
        for state in snapshot['reached']:
            coord = _coerce_state(state)
            if coord is None:
                continue
            r, c = coord
            if can_paint(r, c):
                arr[r, c] = 4

    for key, value in (('reached_F', 4), ('reached_B', 5)):
        for state in snapshot.get(key, []):
            r, c = state
            if can_paint(r, c):
                arr[r, c] = value

    # MARK FRONTIER NODES
    if 'frontier' in snapshot and snapshot['frontier']:
        for state in snapshot['frontier']:
            coord = _coerce_state(state)
            if coord is None:
                continue
            r, c = coord
            if can_paint(r, c):
                arr[r, c] = 6

    for key, value in (('frontier_F', 6), ('frontier_B', 7)):
        for state in snapshot.get(key, []):
            r, c = state
            if can_paint(r, c):
                arr[r, c] = value

    # MARK CURRENT NODE
    current = snapshot.get('current')
    if current:
        r, c = current
        if can_paint(r, c):
            arr[r, c] = 8

    return arr

# FUNCTION TO APPLY FINAL OVERLAYS (FINAL PATH AND TREE)
def _apply_final_overlays(arr: np.ndarray, base_grid: List[List[str]], tree_nodes: Iterable[Tuple[int, int]], final_path: Iterable[Tuple[int, int]] | None) -> np.ndarray:
    result = arr.copy()
    for r, c in tree_nodes:
        if 0 <= r < len(base_grid) and 0 <= c < len(base_grid[0]):
            if base_grid[r][c] in ('S', 'G'):
                continue
            result[r, c] = 10
    if final_path:
        for r, c in final_path:
            if 0 <= r < len(base_grid) and 0 <= c < len(base_grid[0]):
                if base_grid[r][c] in ('S', 'G'):
                    continue
                result[r, c] = 9
    return result

# FUNCTION TO SAVE GIF FROM ARRAYS
def _save_gif_from_arrays(
    arrays: list[np.ndarray],
    snapshots: list[dict],
    base_grid: list[list[str]],
    out_file: str,
    interval: int,
    final_path: list[tuple[int, int]] | None = None,
    tree_nodes: Iterable[tuple[int, int]] | None = None,
    hold_ms: int = 5000,
) -> bool:
    # RETURN FALSE IF NO ARRAYS
    if not arrays:
        return False

    # IMPORT PIL MODULES
    try:
        from PIL import Image, ImagePalette, ImageDraw, ImageFont
    except ImportError:
        return False

    # CONVERT HEX PALETTE TO RGB
    palette_rgb: list[int] = []
    for color in PALETTE:
        palette_rgb.extend(int(color[i:i + 2], 16) for i in (1, 3, 5))
    palette_rgb.extend([0] * (256 * 3 - len(palette_rgb)))

    # CREATE IMAGE PALETTE
    palette = ImagePalette.ImagePalette(mode='RGB')
    palette.palette = bytes(palette_rgb)
    palette_bytes = palette.tobytes()

    # LOAD DEFAULT FONT
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # SET SCALE AND LEGEND DIMENSIONS
    scale = 16
    legend_width = 260
    footer_height = 80

    # INITIALIZE FRAMES AND DURATIONS
    frames = []
    durations: list[int] = []

    # ITERATE OVER ARRAYS
    for idx, arr in enumerate(arrays):
        grid = Image.fromarray(arr, mode='P')
        grid.putpalette(palette_rgb)
        grid = grid.resize((arr.shape[1] * scale, arr.shape[0] * scale), resample=Image.NEAREST)

        # DEFINE LEGEND ITEMS
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

        # SET LEGEND BOX PARAMETERS
        box = 18
        spacing = 8
        legend_height = 10 + len(legend_items) * (box + spacing)
        canvas_height = max(grid.height + footer_height, legend_height + 10)

        # CREATE CANVAS
        canvas = Image.new('P', (grid.width + legend_width, canvas_height), color=1)
        canvas.putpalette(palette_rgb)
        canvas.paste(grid, (0, 0))

        draw = ImageDraw.Draw(canvas)

        # DRAW LEGEND
        legend_x = grid.width + 10
        legend_y = 10
        for label, color_idx in legend_items:
            y0 = legend_y
            y1 = legend_y + box
            draw.rectangle([legend_x, y0, legend_x + box, y1], fill=color_idx, outline=0)
            draw.text((legend_x + box + 6, legend_y), label, fill=0, font=font)
            legend_y += box + spacing

        # DRAW STATS
        stats = snapshots[idx] if idx < len(snapshots) else {}
        stats_text = (
            f"Expanded: {stats.get('nodes_expanded', '?')}  "
            f"Event: {stats.get('event', '')}  "
            f"Direction: {stats.get('direction', '')}"
        )
        draw.text((10, grid.height + 15), stats_text, fill=0, font=font)

        # STORE PALETTE AND ADD FRAME
        canvas.info['palette'] = palette_bytes
        frames.append(canvas)
        durations.append(max(1, interval))

    # ADJUST LAST FRAME DURATION
    if durations:
        durations[-1] = max(hold_ms, durations[-1])

    # SAVE GIF
    frames[0].info['palette'] = palette_bytes
    frames[0].save(
        out_file,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )
    return True

# FUNCTION TO VISUALIZE MAZE SEARCH
def visualize(
    maze_file: str,
    f: Callable[[Node], float],
    interval: int = 100,
    out_file: str | None = None,
    max_steps: int | None = None,
    precompute: bool = False,
    precomputed_snapshots: list[dict] | None = None,
    final_path: Iterable[tuple[int, int]] | None = None,
    tree_nodes: Iterable[tuple[int, int]] | None = None,
    final_hold_ms: int = 5000,
) -> None:
    global _LAST_ANIMATION

    # READ MAZE AND INITIALIZE PROBLEM
    matrix = read_matrix_from_file(maze_file)
    maze = Maze(matrix)
    problem = MazeProblem(maze)

    # DEFINE COLORMAP AND LEGEND
    cmap = ListedColormap(PALETTE)
    legend_handles = [
        mpatches.Patch(facecolor=PALETTE[i], edgecolor='black', label=label)
        for i, label in enumerate([
            'Wall', 
            'Free', 
            'Start', 
            'Goal',
            'Reached Forward', 
            'Reached Backward',
            'Frontier Forward', 
            'Frontier Backward',
            'Current Node', 
            'Final Path', 
            'Search Tree'
        ])
    ]

    should_precompute = precompute or (out_file is not None) or (precomputed_snapshots is not None)
    snapshots: list[dict] = precomputed_snapshots[:] if precomputed_snapshots else []

    # PRECOMPUTE FRAMES IF NECESSARY
    if should_precompute and not snapshots:
        gen = best_first_search_steps(problem, f)
        steps = 0
        try:
            while True:
                if max_steps is not None and steps >= max_steps:
                    break
                snapshots.append(next(gen))
                steps += 1
        except StopIteration:
            pass
        if not snapshots:
            print('No frames produced by the search.')
            return

    # SETUP FIGURE AND AXIS
    use_agg_canvas = False
    try:
        has_display = os.environ.get('DISPLAY') and plt.get_backend().lower() not in ('agg',)
    except Exception:
        has_display = False
    if out_file is not None or threading.current_thread() is not threading.main_thread():
        use_agg_canvas = True

    if use_agg_canvas:
        from matplotlib.figure import Figure
        try:
            from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        except Exception:
            FigureCanvas = None

        if FigureCanvas is not None:
            fig = Figure(figsize=(8, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
        else:
            fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig, ax = plt.subplots(figsize=(8, 6))

    # CONFIG AXIS
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Search visualization')
    fig.subplots_adjust(right=0.65)
    ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1.15, 0.5))

    # COMPUTE FINAL PATH AND TREE
    final_path_coords: list[tuple[int, int]] | None = [tuple(coord) for coord in final_path] if final_path else None
    tree_nodes_set: set[tuple[int, int]] | None = set(tuple(coord) for coord in tree_nodes) if tree_nodes else None

    if should_precompute:
        computed_tree: set[tuple[int, int]] = set()
        for snap in snapshots:
            if snap.get('reached'):
                computed_tree.update(snap['reached'])
            for key in ('reached_F', 'reached_B'):
                if key in snap:
                    computed_tree.update(tuple(state) for state in snap[key])
        if tree_nodes_set is None:
            tree_nodes_set = computed_tree
        else:
            tree_nodes_set = set(tree_nodes_set)
    tree_nodes_set = tree_nodes_set or set()

    # CONVERT SNAPSHOTS TO ARRAYS
    frame_arrays: list[np.ndarray] | None = None
    if should_precompute:
        frame_arrays = [snapshot_to_array(s, matrix) for s in snapshots]
        if frame_arrays:
            frame_arrays.append(_apply_final_overlays(frame_arrays[-1], matrix, tree_nodes_set, final_path_coords))

    # CREATE IMAGE DISPLAY
    im = ax.imshow(frame_arrays[0] if frame_arrays else snapshot_to_array(snapshots[0], matrix),
                   cmap=cmap, vmin=0, vmax=len(PALETTE)-1, interpolation='nearest', origin='upper')

    # DEFINE UPDATE FUNCTION
    def update_frame(idx: int):
        arr = frame_arrays[idx] if frame_arrays else snapshot_to_array(snapshots[idx], matrix)
        im.set_data(arr)
        snap = snapshots[idx]
        dir_label = snap.get('direction') or ''
        ax.set_xlabel(
            f"Nodes expanded: {snap.get('nodes_expanded', '?')}  "
            f"Event: {snap.get('event', '')}  Direction: {dir_label}"
        )
        return im,

    # CREATE ANIMATION
    ani: animation.FuncAnimation | None = None
    if frame_arrays:
        ani = animation.FuncAnimation(fig, update_frame, frames=len(frame_arrays), interval=interval, blit=False)

    # SHOW OR SAVE ANIMATION
    if out_file is None and has_display:
        _LAST_ANIMATION = ani
        plt.show()
    else:
        plt.close(fig)
        saved = False
        if out_file and frame_arrays:
            try:
                if _save_gif_from_arrays(frame_arrays, snapshots, matrix, out_file, interval, final_path_coords, tree_nodes_set, final_hold_ms):
                    print('Animation saved to', out_file)
                    saved = True
            except Exception as exc:
                print('Custom GIF saver failed, falling back to Matplotlib writers:', exc)
        if out_file and not saved and ani:
            try:
                ani.save(out_file, writer='ffmpeg', fps=max(1, int(1000 / interval)))
                print('Animation saved to', out_file)
            except Exception:
                try:
                    ani.save(out_file, writer='pillow', fps=max(1, int(1000 / interval)))
                    print('Animation saved to', out_file)
                except Exception:
                    print('Could not save animation automatically. Try installing ffmpeg or Pillow.')

    if ani is not None:
        _LAST_ANIMATION = ani


# ENTRY POINT FOR MAZE VISUALIZATION
if __name__ == '__main__':
    import argparse

    # CREATE ARGUMENT PARSER
    parser = argparse.ArgumentParser(description='Visualize maze search (matrix view)')
    
    # MAZE FILE PATH
    parser.add_argument('--maze', default='data/input/maze.txt', help='Path to maze file')
    
    # OUTPUT FILE NAME (GIF/MP4)
    parser.add_argument('--out', default=None, help='Output filename (gif/mp4)')
    
    # FRAME INTERVAL IN MILLISECONDS
    parser.add_argument('--interval', type=int, default=150, help='Frame interval in ms')
    
    # MAX FRAMES TO PRECOMPUTE
    parser.add_argument('--max-steps', type=int, default=None, help='Max frames to precompute')
    
    # FLAG TO PRECOMPUTE ALL FRAMES BEFORE ANIMATION
    parser.add_argument('--precompute', action='store_true', help='Precompute all frames before animating/saving')
    
    # PARSE ARGUMENTS
    args = parser.parse_args()

    # CALL VISUALIZE FUNCTION WITH ARGUMENTS
    visualize(
        maze_file=args.maze,
        f=lambda n: n.g,
        interval=args.interval,
        out_file=args.out,
        max_steps=args.max_steps,
        precompute=args.precompute,
    )
