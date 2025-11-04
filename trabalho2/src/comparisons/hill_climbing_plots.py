# IMPORTS EXTERNAL
from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Tuple
import matplotlib.pyplot as plt
import numpy as np

# DEFAULT ALGORITHM MAP FOR PLOTTING
DEFAULT_ALG_MAP: Tuple[Tuple[str, str], ...] = (
    ("Sideways (10)", "Sideways-10"),
    ("Sideways (100)", "Sideways-100"),
    ("Restarts + Sideways", "RandomRestartsSideways"),
    ("Restarts + Hill", "RandomRestartsHill"),
    ("SA Linear", "SimulatedAnnealingLinear"),
    ("SA Exp", "SimulatedAnnealingExponential"),
)

# ENSURE DIRECTORY EXISTS
def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

# PARSE SUCCESS RATIO FROM STRING
def _parse_success(value: str) -> float:
    try:
        succeeded, total = value.split("/")
        return float(succeeded) / float(total)
    except Exception:
        return 0.0

# -------------------------------
# FUNÇÃO PRINCIPAL
# -------------------------------
def plot_hill_climbing_metrics(
    metrics: Dict[str, str],
    *,
    out_dir: Path | None = None,
    algorithms: Iterable[Tuple[str, str]] = DEFAULT_ALG_MAP,
) -> None:
    if out_dir is None:
        repo_root = Path(__file__).resolve().parents[2]
        out_dir = repo_root / "data" / "output" / "graphics"
    _ensure_dir(out_dir)

    # ----- GERAL -----
    labels = [label for label, _ in algorithms]

    data = {
        "Average time (ms)": [float(metrics.get(f"{key} avg time (ms)", 0.0)) for _, key in algorithms],
        # "Average memory (B)": [float(metrics.get(f"{key} avg memory (B)", 0.0)) for _, key in algorithms],
        "Average peak (KB)": [float(metrics.get(f"{key} avg peak (KB)", 0.0)) for _, key in algorithms],
        "Average current (KB)": [float(metrics.get(f"{key} avg current (KB)", 0.0)) for _, key in algorithms],
        "Average conflicts": [float(metrics.get(f"{key} avg conflicts", 0.0)) for _, key in algorithms],
        "Average steps": [float(metrics.get(f"{key} avg steps", 0.0)) for _, key in algorithms],
        "Success rate": [_parse_success(metrics.get(f"{key} success count", "0/1")) for _, key in algorithms],
    }

    for title, values in data.items():
        print(title)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(labels, values, color="#3498db")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.tick_params(axis="x", rotation=20)
        if "rate" in title.lower():
            ax.set_ylim(0, 1)
        fig.tight_layout()
        clean_title = title.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename = f"general_{clean_title}.png"
        save_path = out_dir / "general" / filename
        fig.savefig(save_path, dpi=160)
        print(f"Salvo em: {save_path}")
        plt.close(fig)

    # ----- COMPARAÇÕES -----
    comparisons = [
        ("Sideways-10", "Sideways-100", "Sideways-Comparison", [
            "avg time (ms)", 
            # "avg memory (B)", 
            "avg peak (KB)", 
            "avg current (KB)",
            "avg conflicts", 
            # "best conflicts", 
            # "worst conflicts", 
            "avg steps", 
            "success count"
        ]),
        ("RandomRestartsSideways", "RandomRestartsHill", "Restarts-Comparison", [
            "avg time (ms)", 
            # "avg memory (B)", 
            "avg peak (KB)", 
            "avg current (KB)",
            # "avg conflicts", 
            # "best conflicts", 
            # "worst conflicts", 
            "avg steps", 
            "success count",
            "avg restarts", 
            "max moves", 
            "sideways flag"
        ]),
        ("SimulatedAnnealingLinear", "SimulatedAnnealingExponential", "SA-Comparison", [
            "avg time (ms)", 
            # "avg memory (B)", 
            "avg peak (KB)", 
            "avg current (KB)",
            # "avg conflicts", 
            # "best conflicts", 
            # "worst conflicts", 
            "avg steps", 
            "success count",
            "temperature", 
            "max steps"
        ]),
    ]

    for algo1, algo2, fname, fields in comparisons:
        metrics1, metrics2 = [], []
        for field in fields:
            v1 = metrics.get(f"{algo1} {field}", "0")
            v2 = metrics.get(f"{algo2} {field}", "0")
            if "success" in field:
                metrics1.append(_parse_success(v1))
                metrics2.append(_parse_success(v2))
            else:
                metrics1.append(float(v1))
                metrics2.append(float(v2))

        x = np.arange(len(fields))
        width = 0.35

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.bar(x - width/2, metrics1, width, label=algo1, color="#3498db")
        ax.bar(x + width/2, metrics2, width, label=algo2, color="#e67e22")

        ax.set_title(f"{algo1} vs {algo2}", fontsize=13, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(fields, rotation=25, ha="right")
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        save_path = out_dir / "comparisons" / f"{fname}.png"
        fig.savefig(out_dir / "comparisons" / f"{fname}.png", dpi=160)
        print(f"Salvo em: {save_path}")
        plt.close(fig)


__all__ = ["plot_hill_climbing_metrics"]
