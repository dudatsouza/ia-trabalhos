"""Matrix visualization helpers for maze search animations."""
from __future__ import annotations

from typing import Callable, Dict, Any, List, Tuple, Iterable
import heapq
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

from maze_representation import Maze
from maze_generator import read_matrix_from_file
from maze_problem import MazeProblem
from node import Node

Snapshot = Dict[str, Any]

# Fixed palette indices used by snapshot_to_array and GIF saver.
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

_LAST_ANIMATION: animation.FuncAnimation | None = None


def best_first_search_steps(problem: MazeProblem, f: Callable[[Node], float]) -> Iterable[Snapshot]:
    """Yield snapshots for a generic best-first search run."""
    start = Node(state=problem.initial, g=0.0, h=problem.heuristic(problem.initial))
    frontier: List[Tuple[float, Node]] = []
    heapq.heappush(frontier, (f(start), start))
    reached: Dict[Any, Node] = {start.state: start}
    nodes_expanded = 0

    def make_snapshot(current: Node | None, event: str) -> Snapshot:
        return {
            'current': current.state if current else None,
            'frontier': [(n.state, float(priority)) for priority, n in frontier],
            'reached': {s: node.g for s, node in reached.items()},
            'parents': {s: node.parent.state if node.parent else None for s, node in reached.items()},
            'nodes_expanded': nodes_expanded,
            'event': event,
        }

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


def snapshot_to_array(
    snapshot: Snapshot,
    base_grid: List[List[str]],
    allow_override_start_goal: bool = False,
) -> np.ndarray:
    """Map snapshot content to palette indices."""
    height = len(base_grid)
    width = len(base_grid[0])
    arr = np.zeros((height, width), dtype=np.uint8)

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

    def can_paint(row: int, col: int) -> bool:
        if allow_override_start_goal:
            return True
        return base_grid[row][col] not in ('S', 'G')

    if 'reached' in snapshot and snapshot['reached']:
        for state in snapshot['reached']:
            r, c = state
            if can_paint(r, c):
                arr[r, c] = 4

    for key, value in (('reached_F', 4), ('reached_B', 5)):
        for state in snapshot.get(key, []):
            r, c = state
            if can_paint(r, c):
                arr[r, c] = value

    if 'frontier' in snapshot and snapshot['frontier']:
        for state, _priority in snapshot['frontier']:
            r, c = state
            if can_paint(r, c):
                arr[r, c] = 6

    for key, value in (('frontier_F', 6), ('frontier_B', 7)):
        for state in snapshot.get(key, []):
            r, c = state
            if can_paint(r, c):
                arr[r, c] = value

    current = snapshot.get('current')
    if current:
        r, c = current
        if can_paint(r, c):
            arr[r, c] = 8

    return arr


def _apply_final_overlays(
    arr: np.ndarray,
    base_grid: List[List[str]],
    tree_nodes: Iterable[Tuple[int, int]],
    final_path: Iterable[Tuple[int, int]] | None,
) -> np.ndarray:
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


def _save_gif_from_arrays(
    arrays: List[np.ndarray],
    snapshots: List[Snapshot],
    base_grid: List[List[str]],
    out_file: str,
    interval: int,
    final_path: List[Tuple[int, int]] | None = None,
    tree_nodes: Iterable[Tuple[int, int]] | None = None,
    hold_ms: int = 5000,
) -> bool:
    """Write a GIF with legend, stats, final path, and search tree while preserving colors."""
    if not arrays:
        return False

    try:
        from PIL import Image, ImagePalette, ImageDraw, ImageFont
    except ImportError:
        return False

    palette_rgb: List[int] = []
    for color in PALETTE:
        palette_rgb.extend(int(color[i:i + 2], 16) for i in (1, 3, 5))
    palette_rgb.extend([0] * (256 * 3 - len(palette_rgb)))
    palette = ImagePalette.ImagePalette(mode='RGB')
    palette.palette = bytes(palette_rgb)
    palette_bytes = palette.tobytes()

    try:
        font = ImageFont.load_default()
    except Exception:  # pragma: no cover - Pillow always ships default font
        font = None

    scale = 16
    legend_width = 260
    footer_height = 80

    frames = []
    durations: List[int] = []
    for idx, arr in enumerate(arrays):
        grid = Image.fromarray(arr, mode='P')
        grid.putpalette(palette_rgb)
        grid = grid.resize((arr.shape[1] * scale, arr.shape[0] * scale), resample=Image.NEAREST)

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

        box = 18
        spacing = 8
        legend_height = 10 + len(legend_items) * (box + spacing)
        canvas_height = max(grid.height + footer_height, legend_height + 10)

        canvas = Image.new('P', (grid.width + legend_width, canvas_height), color=1)
        canvas.putpalette(palette_rgb)
        canvas.paste(grid, (0, 0))

        draw = ImageDraw.Draw(canvas)

        legend_x = grid.width + 10
        legend_y = 10
        for label, color_idx in legend_items:
            y0 = legend_y
            y1 = legend_y + box
            draw.rectangle([legend_x, y0, legend_x + box, y1], fill=color_idx, outline=0)
            draw.text((legend_x + box + 6, legend_y), label, fill=0, font=font)
            legend_y += box + spacing

        stats = snapshots[idx] if idx < len(snapshots) else {}
        stats_text = (
            f"Expanded: {stats.get('nodes_expanded', '?')}  "
            f"Event: {stats.get('event', '')}  "
            f"Direction: {stats.get('direction', '')}"
        )
        draw.text((10, grid.height + 15), stats_text, fill=0, font=font)

        canvas.info['palette'] = palette_bytes
        frames.append(canvas)
        durations.append(max(1, interval))

    if durations:
        durations[-1] = max(hold_ms, durations[-1])

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


def visualize(
    maze_file: str,
    f: Callable[[Node], float],
    interval: int = 200,
    out_file: str | None = None,
    max_steps: int | None = None,
    precompute: bool = False,
    precomputed_snapshots: List[Snapshot] | None = None,
    final_path: Iterable[Tuple[int, int]] | None = None,
    tree_nodes: Iterable[Tuple[int, int]] | None = None,
    final_hold_ms: int = 5000,
) -> None:
    """Render or save an animation for a maze search run."""
    global _LAST_ANIMATION
    matrix = read_matrix_from_file(maze_file)
    maze = Maze(matrix)
    problem = MazeProblem(maze)

    cmap = ListedColormap(PALETTE)
    legend_handles = [
        mpatches.Patch(facecolor=PALETTE[0], edgecolor='black', label='Wall'),
        mpatches.Patch(facecolor=PALETTE[1], edgecolor='black', label='Free'),
        mpatches.Patch(facecolor=PALETTE[2], edgecolor='black', label='Start'),
        mpatches.Patch(facecolor=PALETTE[3], edgecolor='black', label='Goal'),
        mpatches.Patch(facecolor=PALETTE[4], edgecolor='black', label='Reached Forward'),
        mpatches.Patch(facecolor=PALETTE[5], edgecolor='black', label='Reached Backward'),
        mpatches.Patch(facecolor=PALETTE[6], edgecolor='black', label='Frontier Forward'),
        mpatches.Patch(facecolor=PALETTE[7], edgecolor='black', label='Frontier Backward'),
        mpatches.Patch(facecolor=PALETTE[8], edgecolor='black', label='Current Node'),
        mpatches.Patch(facecolor=PALETTE[9], edgecolor='black', label='Final Path'),
        mpatches.Patch(facecolor=PALETTE[10], edgecolor='black', label='Search Tree'),
    ]
    should_precompute = precompute or (out_file is not None) or (precomputed_snapshots is not None)
    snapshots: List[Snapshot] = precomputed_snapshots[:] if precomputed_snapshots is not None else []

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

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Search visualization')
    fig.subplots_adjust(right=0.65)
    legend = ax.legend(handles=legend_handles, loc='center left', bbox_to_anchor=(1.15, 0.5))

    frame_arrays: List[np.ndarray] | None = None
    final_path_coords: List[Tuple[int, int]] | None = (
        [tuple(coord) for coord in final_path]
        if final_path is not None
        else None
    )
    tree_nodes_set: set[Tuple[int, int]] | None = (
        set(tuple(coord) for coord in tree_nodes)
        if tree_nodes is not None
        else None
    )

    if should_precompute:
        computed_tree: set[Tuple[int, int]] = set()
        for snap in snapshots:
            if snap.get('reached'):
                computed_tree.update(snap['reached'].keys())
            for key in ('reached_F', 'reached_B'):
                if key in snap:
                    computed_tree.update(tuple(state) for state in snap[key])
        if tree_nodes_set is None:
            tree_nodes_set = computed_tree
        else:
            tree_nodes_set = set(tree_nodes_set)
    tree_nodes_set = tree_nodes_set or set()
    ani: animation.FuncAnimation | None = None
    if should_precompute:
        frame_arrays = [snapshot_to_array(s, matrix) for s in snapshots]
        if frame_arrays:
            final_snapshot = dict(snapshots[-1]) if snapshots else {}
            final_snapshot['event'] = 'final_path'
            final_snapshot['direction'] = 'Summary'
            if snapshots:
                final_snapshot.setdefault('nodes_expanded', snapshots[-1].get('nodes_expanded'))
            if final_path_coords:
                final_snapshot['final_path'] = final_path_coords
            snapshots.append(final_snapshot)
            frame_arrays.append(
                _apply_final_overlays(frame_arrays[-1], matrix, tree_nodes_set, final_path_coords)
            )
        im = ax.imshow(frame_arrays[0], cmap=cmap, vmin=0, vmax=len(PALETTE) - 1, interpolation='nearest', origin='upper')

        def update_from_list(idx: int):
            arr = frame_arrays[idx]
            im.set_data(arr)
            snap = snapshots[idx]
            dir_label = snap.get('direction') or ''
            ax.set_xlabel(
                f"Nodes expanded: {snap.get('nodes_expanded', '?')}  "
                f"Event: {snap.get('event', '')}  Direction: {dir_label}"
            )
            return im,

        def ensure_animation() -> animation.FuncAnimation:
            nonlocal ani
            if ani is None:
                ani = animation.FuncAnimation(
                    fig,
                    update_from_list,
                    frames=len(frame_arrays),
                    interval=interval,
                    blit=False,
                )
            return ani
    else:
        gen = best_first_search_steps(problem, f)
        try:
            first_snapshot = next(gen)
        except StopIteration:
            print('Search produced no frames.')
            plt.close(fig)
            return

        im = ax.imshow(snapshot_to_array(first_snapshot, matrix), cmap=cmap, vmin=0, vmax=len(PALETTE) - 1, interpolation='nearest', origin='upper')

        def update_stream(_idx: int):
            try:
                snap = next(gen)
            except StopIteration:
                return im,
            im.set_data(snapshot_to_array(snap, matrix))
            dir_label = snap.get('direction') or ''
            ax.set_xlabel(
                f"Nodes expanded: {snap.get('nodes_expanded', '?')}  "
                f"Event: {snap.get('event', '')}  Direction: {dir_label}"
            )
            return im,

        ani = animation.FuncAnimation(fig, update_stream, interval=interval, blit=False, cache_frame_data=False)

    has_display = os.environ.get('DISPLAY') and plt.get_backend().lower() not in ('agg',)
    if out_file is None and has_display:
        if should_precompute:
            ani_to_keep = ensure_animation()
        else:
            ani_to_keep = ani
        _LAST_ANIMATION = ani_to_keep
        plt.show()
    else:
        plt.close(fig)

    saved = False
    if out_file and frame_arrays is not None:
        try:
            if _save_gif_from_arrays(
                frame_arrays,
                snapshots,
                matrix,
                out_file,
                interval,
                final_path_coords,
                tree_nodes_set or set(),
                final_hold_ms,
            ):
                print('Animation saved to', out_file)
                saved = True
        except Exception as exc:
            print('Custom GIF saver failed, falling back to Matplotlib writers:', exc)

    if out_file and not saved:
        if should_precompute:
            ani_to_keep = ensure_animation()
        else:
            ani_to_keep = ani
        _LAST_ANIMATION = ani_to_keep
        try:
            ani_to_keep.save(out_file, writer='ffmpeg', fps=max(1, int(1000 / interval)))
            print('Animation saved to', out_file)
            saved = True
        except Exception:
            try:
                ani_to_keep.save(out_file, writer='pillow', fps=max(1, int(1000 / interval)))
                print('Animation saved to', out_file)
                saved = True
            except Exception:
                print('Could not save animation automatically. Try installing ffmpeg or Pillow.')

    if ani is not None:
        _LAST_ANIMATION = ani


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Visualize maze search (matrix view)')
    parser.add_argument('--maze', default='data/input/maze.txt', help='Path to maze file')
    parser.add_argument('--out', default=None, help='Output filename (gif/mp4).')
    parser.add_argument('--interval', type=int, default=150, help='Frame interval in ms')
    parser.add_argument('--max-steps', type=int, default=None, help='Max frames to precompute')
    parser.add_argument('--precompute', action='store_true', help='Precompute all frames before animating/saving')
    args = parser.parse_args()

    visualize(
        args.maze,
        f=lambda n: n.g,
        interval=args.interval,
        out_file=args.out,
        max_steps=args.max_steps,
        precompute=args.precompute,
    )
