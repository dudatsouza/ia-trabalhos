from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import matplotlib.pyplot as plt

DEFAULT_ALG_MAP: Tuple[Tuple[str, str], ...] = (
    ("Sideways (10)", "Sideways-10"),
    ("Sideways (100)", "Sideways-100"),
    ("Restarts + Sideways", "RandomRestartsSideways"),
    ("Restarts + Hill", "RandomRestartsHill"),
    ("SA Linear", "SimulatedAnnealingLinear"),
    ("SA Exp", "SimulatedAnnealingExponential"),
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _parse_success(value: str) -> float:
    try:
        succeeded, total = value.split("/")
        return float(succeeded) / float(total)
    except Exception:
        return 0.0


def plot_hill_climbing_metrics(
    metrics: Dict[str, str],
    *,
    out_dir: Path | None = None,
    algorithms: Iterable[Tuple[str, str]] = DEFAULT_ALG_MAP,
) -> None:
    if out_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        out_dir = repo_root / "data" / "output" / "graphics" / "hill_climbing"
    _ensure_dir(out_dir)

    labels = [label for label, _ in algorithms]

    times = [float(metrics.get(f"{key} avg time (ms)", 0.0)) for _, key in algorithms]
    conflicts = [float(metrics.get(f"{key} avg conflicts", 0.0)) for _, key in algorithms]
    success_rates = [
        _parse_success(metrics.get(f"{key} success count", "0/1")) for _, key in algorithms
    ]
    steps = [float(metrics.get(f"{key} avg steps", 0.0)) for _, key in algorithms]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()

    axes[0].bar(labels, times, color="#3498db")
    axes[0].set_title("Average time (ms)")
    axes[0].set_ylabel("ms")
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].bar(labels, conflicts, color="#e67e22")
    axes[1].set_title("Average conflicts")
    axes[1].set_ylabel("Conflicts")
    axes[1].tick_params(axis="x", rotation=20)

    axes[2].bar(labels, success_rates, color="#27ae60")
    axes[2].set_title("Success rate")
    axes[2].set_ylabel("Ratio")
    axes[2].set_ylim(0, 1)
    axes[2].tick_params(axis="x", rotation=20)

    axes[3].bar(labels, steps, color="#9b59b6")
    axes[3].set_title("Average steps")
    axes[3].set_ylabel("Iterations")
    axes[3].tick_params(axis="x", rotation=20)

    fig.tight_layout()
    fig.savefig(out_dir / "hill_climbing_metrics.png", dpi=160)
    plt.close(fig)


__all__ = ["plot_hill_climbing_metrics"]
