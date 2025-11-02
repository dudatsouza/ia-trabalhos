from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from core.eight_queens_representation import EightQueensProblem

from greedy_local_search.hill_climbing import hill_climbing
from greedy_local_search.random_restarts import hill_climbing_with_random_restarts
from greedy_local_search.sideways_moves import hill_climbing_with_sideways_moves
from greedy_local_search.simulated_annealing import simulated_annealing

from tools.measure_time_memory import measure_time_memory

try:
	from comparisons.hill_climbing_plots import plot_hill_climbing_metrics
except Exception:  # pragma: no cover - plotting is optional
	plot_hill_climbing_metrics = None  # type: ignore


@dataclass
class RunStats:
	elapsed_ms: float
	rss_delta: float
	current_bytes: float
	peak_bytes: float
	final_conflicts: int
	steps: int
	extra: Dict[str, float]


def _default_metrics(num_runs: int) -> Dict[str, str]:
	return {
		"runs": str(num_runs),
	}


def _summarize(
	label: str,
	stats: List[RunStats],
	successes: int,
) -> Dict[str, str]:
	if not stats:
		return {}

	times = [s.elapsed_ms for s in stats]
	rss = [s.rss_delta for s in stats]
	peaks = [s.peak_bytes for s in stats]
	currents = [s.current_bytes for s in stats]
	conflicts = [s.final_conflicts for s in stats]
	steps = [s.steps for s in stats]

	metrics = {
		f"{label} avg time (ms)": f"{statistics.fmean(times):.3f}",
		f"{label} avg memory (B)": f"{statistics.fmean(rss):.3f}",
		f"{label} avg peak (KB)": f"{statistics.fmean(peaks) / 1024:.3f}",
		f"{label} avg current (KB)": f"{statistics.fmean(currents) / 1024:.3f}",
		f"{label} avg conflicts": f"{statistics.fmean(conflicts):.3f}",
		f"{label} best conflicts": str(min(conflicts)),
		f"{label} worst conflicts": str(max(conflicts)),
		f"{label} avg steps": f"{statistics.fmean(steps):.1f}",
		f"{label} success count": f"{successes}/{len(stats)}",
	}

	# Include any algorithm-specific aggregates
	extras: Dict[str, List[float]] = {}
	for s in stats:
		for key, value in s.extra.items():
			extras.setdefault(key, []).append(value)

	for key, values in extras.items():
		metrics[f"{label} {key}"] = f"{statistics.fmean(values):.3f}"

	return metrics


def compare_hill_climbing_algorithms(
	*,
	num_runs: int = 30,
	sideways_limit: int = 100,
	random_allow_sideways: bool = True,
	random_max_moves: int = 100,
	random_max_restarts: int = 100,
	annealing_temperature: float = 100.0,
	annealing_cooling: int = 2
) -> Dict[str, str]:
	"""Runs multiple hill-climbing variants and returns aggregated metrics."""

	metrics: Dict[str, str] = _default_metrics(num_runs)

	# Basic Hill Climbing
	hill_stats: List[RunStats] = []
	hill_success = 0

	for _ in range(num_runs):
		problem = EightQueensProblem()
		result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
			hill_climbing,
			problem,
			False,
		)
		board, history, _ = result
		final_conflicts = problem.conflicts(board)
		if final_conflicts == 0:
			hill_success += 1

		hill_stats.append(
			RunStats(
				elapsed_ms=elapsed,
				rss_delta=memory_used,
				current_bytes=current_bytes,
				peak_bytes=peak_bytes,
				final_conflicts=final_conflicts,
				steps=len(history),
				extra={},
			)
		)

	metrics.update(_summarize("HillClimbing", hill_stats, hill_success))

	# Sideways Moves
	sideways_stats: List[RunStats] = []
	sideways_success = 0

	for _ in range(num_runs):
		problem = EightQueensProblem()
		result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
			hill_climbing_with_sideways_moves,
			problem,
			sideways_limit,
			False,
		)
		board, history, _ = result
		final_conflicts = problem.conflicts(board)
		if final_conflicts == 0:
			sideways_success += 1

		sideways_stats.append(
			RunStats(
				elapsed_ms=elapsed,
				rss_delta=memory_used,
				current_bytes=current_bytes,
				peak_bytes=peak_bytes,
				final_conflicts=final_conflicts,
				steps=len(history),
				extra={"max sideways": float(sideways_limit)},
			)
		)

	metrics.update(_summarize("Sideways", sideways_stats, sideways_success))

	# Random Restarts
	restart_stats: List[RunStats] = []
	restart_success = 0

	for _ in range(num_runs):
		problem = EightQueensProblem()
		result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
			hill_climbing_with_random_restarts,
			problem,
			random_allow_sideways,
			random_max_moves,
			random_max_restarts,
			False,
		)

		board, fitness, restart_count, history, _ = result
		final_conflicts = problem.conflicts(board) if board else int(-fitness)
		if final_conflicts == 0:
			restart_success += 1

		restart_stats.append(
			RunStats(
				elapsed_ms=elapsed,
				rss_delta=memory_used,
				current_bytes=current_bytes,
				peak_bytes=peak_bytes,
				final_conflicts=final_conflicts,
				steps=len(history) if history else 0,
				extra={"avg restarts": float(restart_count)},
			)
		)

	metrics.update(_summarize("RandomRestarts", restart_stats, restart_success))

	# Simulated Annealing
	annealing_stats: List[RunStats] = []
	annealing_success = 0

	for _ in range(num_runs):
		problem = EightQueensProblem()
		result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
			simulated_annealing,
			problem,
			annealing_temperature,
			annealing_cooling,
			False
		)
		board, fitness, history, _ = result
		final_conflicts = problem.conflicts(board)
		if final_conflicts == 0:
			annealing_success += 1

		annealing_stats.append(
			RunStats(
				elapsed_ms=elapsed,
				rss_delta=memory_used,
				current_bytes=current_bytes,
				peak_bytes=peak_bytes,
				final_conflicts=final_conflicts,
				steps=len(history),
				extra={"temperature": float(annealing_temperature)},
			)
		)

	metrics.update(_summarize("SimulatedAnnealing", annealing_stats, annealing_success))

	repo_root = Path(__file__).resolve().parents[2]
	output_dir = repo_root / "data" / "output" / "metrics"
	output_dir.mkdir(parents=True, exist_ok=True)
	metrics_path = output_dir / "metrics_hill_climbing.json"

	with metrics_path.open("w", encoding="utf-8") as fh:
		json.dump(metrics, fh, indent=4, ensure_ascii=False)

	if plot_hill_climbing_metrics:
		try:
			plot_hill_climbing_metrics(metrics, out_dir=repo_root / "data" / "output" / "graphics" / "hill_climbing")
		except Exception:
			pass

	return metrics


__all__ = ["compare_hill_climbing_algorithms"]
