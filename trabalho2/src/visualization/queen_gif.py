from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from PIL import Image, ImageDraw, ImageFont

BOARD_SIZE = 8
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"
HIGHLIGHT_FROM = "#f9e79f"
HIGHLIGHT_TO = "#82e0aa"
HEADER_BG = "#ffffff"
HEADER_TEXT = "#333333"
QUEEN_FILL = "#1b2631"
QUEEN_OUTLINE = "#f7f9f9"
BEST_CANDIDATE_COLOR = "#f5b7b1"


def _load_font(cell_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Tries to load a readable font for the queens and header."""

    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", int(cell_size * 0.72))
    except Exception:
        return ImageFont.load_default()


def _load_header_font(cell_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", int(cell_size * 0.32))
    except Exception:
        return ImageFont.load_default()


def diff_states(
    previous: Sequence[int],
    current: Sequence[int],
) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
    """Returns the moved queen coordinates as ((row, col) from, (row, col) to)."""

    moved_from: Optional[Tuple[int, int]] = None
    moved_to: Optional[Tuple[int, int]] = None

    for col, (row_prev, row_curr) in enumerate(zip(previous, current)):
        if row_prev != row_curr:
            moved_from = (row_prev, col)
            moved_to = (row_curr, col)
            break

    return moved_from, moved_to


def board_to_image(
    board: Sequence[int],
    *,
    conflicts: Optional[int] = None,
    step_index: Optional[int] = None,
    highlight: Optional[Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]] = None,
    square_conflicts: Optional[Dict[Tuple[int, int], int]] = None,
    best_candidates: Optional[Set[Tuple[int, int]]] = None,
    cell_size: int = 80,
) -> Image.Image:
    """Renders a chess board with queens for a specific step."""

    n = len(board)
    if n == 0:
        raise ValueError("Board cannot be empty")

    margin = int(cell_size * 0.2)
    header_height = int(cell_size * 0.9)
    board_px = n * cell_size
    width = board_px + 2 * margin
    height = board_px + header_height + 2 * margin

    image = Image.new("RGB", (width, height), HEADER_BG)
    draw = ImageDraw.Draw(image)

    board_top = margin + header_height
    font = _load_font(cell_size)
    header_font = _load_header_font(cell_size)

    # Header text
    header_lines: List[str] = []
    if step_index is not None:
        header_lines.append(f"Step {step_index + 1}")
    if conflicts is not None:
        header_lines.append(f"Conflicts: {conflicts}")

    if header_lines:
        header_text = " | ".join(header_lines)
        text_bbox = draw.textbbox((0, 0), header_text, font=header_font)
        text_x = (width - (text_bbox[2] - text_bbox[0])) // 2
        text_y = (header_height - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), header_text, font=header_font, fill=HEADER_TEXT)

    moved_from, moved_to = highlight if highlight else (None, None)

    # Draw squares
    for row in range(n):
        for col in range(n):
            base_color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
            x0 = margin + col * cell_size
            y0 = board_top + row * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            fill = base_color
            if moved_from == (row, col):
                fill = HIGHLIGHT_FROM
            elif moved_to == (row, col):
                fill = HIGHLIGHT_TO
            elif best_candidates and (row, col) in best_candidates:
                fill = BEST_CANDIDATE_COLOR

            draw.rectangle([x0, y0, x1, y1], fill=fill, outline="#2c3e50", width=2)

            if square_conflicts and (row, col) in square_conflicts:
                conflict_value = square_conflicts[(row, col)]
                text = str(conflict_value)
                text_bbox = draw.textbbox((0, 0), text, font=header_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                draw.text(
                    (x0 + cell_size / 2 - text_width / 2, y0 + cell_size / 2 - text_height / 2),
                    text,
                    font=header_font,
                    fill="#1c2833",
                )

    # Draw queens
    for col, row in enumerate(board):
        x0 = margin + col * cell_size
        y0 = board_top + row * cell_size
        cx = x0 + cell_size / 2
        cy = y0 + cell_size / 2
        radius = cell_size * 0.28

        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=QUEEN_FILL,
            outline=QUEEN_OUTLINE,
            width=2,
        )

        q_text = "Q"
        text_bbox = draw.textbbox((0, 0), q_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(
            (cx - text_width / 2, cy - text_height / 2),
            q_text,
            font=font,
            fill=QUEEN_OUTLINE,
        )

    return image


def generate_gif_from_states(
    states: Iterable[Sequence[int]],
    out_path: str | Path,
    *,
    conflicts: Optional[Sequence[int]] = None,
    square_conflicts: Optional[Sequence[Dict[Tuple[int, int], int]]] = None,
    best_candidates: Optional[Sequence[Set[Tuple[int, int]]]] = None,
    duration_ms: int = 300,
    cell_size: int = 80,
) -> str:
    """Creates a GIF highlighting queen moves across the provided states."""

    states_list = [list(state) for state in states]
    if not states_list:
        raise ValueError("No states provided for GIF generation")

    conflict_list: Optional[List[int]] = None
    if conflicts is not None:
        conflict_list = list(conflicts)
        if len(conflict_list) != len(states_list):
            raise ValueError("Length of conflicts does not match number of states")

    conflicts_per_square: Optional[List[Dict[Tuple[int, int], int]]] = None
    if square_conflicts is not None:
        conflicts_per_square = list(square_conflicts)
        if len(conflicts_per_square) != len(states_list):
            raise ValueError("Length of square_conflicts does not match number of states")

    best_candidate_list: Optional[List[Set[Tuple[int, int]]]] = None
    if best_candidates is not None:
        best_candidate_list = [set(item) for item in best_candidates]
        if len(best_candidate_list) != len(states_list):
            raise ValueError("Length of best_candidates does not match number of states")

    images: List[Image.Image] = []
    previous = None

    for idx, state in enumerate(states_list):
        highlight = diff_states(previous, state) if previous is not None else None
        image = board_to_image(
            state,
            conflicts=conflict_list[idx] if conflict_list else None,
            step_index=idx,
            highlight=highlight,
            square_conflicts=conflicts_per_square[idx] if conflicts_per_square else None,
            best_candidates=best_candidate_list[idx] if best_candidate_list else None,
            cell_size=cell_size,
        )
        images.append(image)
        previous = state

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    images[0].save(
        out_path,
        save_all=True,
        append_images=images[1:],
        duration=max(1, duration_ms),
        loop=0,
    )

    return str(out_path)


__all__ = [
    "board_to_image",
    "diff_states",
    "generate_gif_from_states",
]
