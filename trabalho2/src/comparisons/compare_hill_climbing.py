# IMPORTS EXTERNAL
from __future__ import annotations
import json
import random
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

# IMPORTS INTERNAL
# CORE
from core.eight_queens_representation import EightQueensProblem
# TOOLS
from tools.measure_time_memory import measure_time_memory
# LOCAL SEARCH
from local_search.random_restarts import hill_climbing_with_random_restarts
from local_search.sideways_moves import hill_climbing_with_sideways_moves
from local_search.simulated_annealing import simulated_annealing
# COMPARISONS PLOTTING (OPTIONAL)
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

# DEFAULT METRICS DICTIONARY
def _default_metrics(num_runs: int) -> Dict[str, str]:
	return {
		"runs": str(num_runs),
	}

# SUMMARIZE A LIST OF RUN STATS INTO AGGREGATED METRICS
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
		f"{label}": "",
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

# GENERATE UNIQUE INITIAL BOARDS
def _generate_unique_boards(num_runs: int, seed: int = 42) -> List[Tuple[int, ...]]:
	rng = random.Random(seed)
	boards: List[Tuple[int, ...]] = []
	seen: set[Tuple[int, ...]] = set()
	while len(boards) < num_runs:
		board = list(range(8))
		rng.shuffle(board)
		key = tuple(board)
		if key in seen:
			continue
		seen.add(key)
		boards.append(key)
	return boards

# RUNS THE CONFIGURED HILL-CLIMBING VARIANTS AND RETURNS AGGREGATED METRICS
def compare_hill_climbing_algorithms(
	*,
	num_runs: int = 100,
	sideways_limits: Sequence[int] = (10, 100),
	random_max_moves: int = 20,
	random_max_restarts: int = 100,
	annealing_temperature: float = 400.0,
	annealing_linear_max_steps: int = 1000,
	annealing_exp_max_steps: int = 1000,
) -> Dict[str, str]:
	
	metrics: Dict[str, str] = _default_metrics(num_runs)
	base_boards = _generate_unique_boards(num_runs)
	seed_offsets = {
		"sideways": 1_000,
		"rr_sideways": 2_000,
		"rr_hill": 3_000,
		"anneal_linear": 4_000,
		"anneal_exp": 5_000,
	}

	# SIDEWAYS MOVES VARIANTS
	for limit in sideways_limits:
		sideways_stats: List[RunStats] = []
		sideways_success = 0

		for idx, board_seed in enumerate(base_boards):
			problem = EightQueensProblem()
			result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
				hill_climbing_with_sideways_moves,
				problem,
				limit,
				False,
				initial_board=board_seed,
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
					extra={"sideways limit": float(limit)},
				)
			)

		metrics.update(_summarize(f"Sideways-{limit}", sideways_stats, sideways_success))

	# RANDOM RESTARTS VARIANTS
	for allow_sideways, label in (
		(True, "RandomRestartsSideways"),
		(False, "RandomRestartsHill"),
	):
		restart_stats: List[RunStats] = []
		restart_success = 0

		for idx, board_seed in enumerate(base_boards):
			problem = EightQueensProblem()
			rng_seed = seed_offsets["rr_sideways" if allow_sideways else "rr_hill"] + idx
			rng = random.Random(rng_seed)
			result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
				hill_climbing_with_random_restarts,
				problem,
				allow_sideways,
				random_max_moves,
				random_max_restarts,
				False,
				initial_board=board_seed,
				rng=rng,
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
					extra={
						"avg restarts": float(restart_count),
						"max moves": float(random_max_moves),
						"sideways flag": float(1 if allow_sideways else 0),
					},
				)
			)

		metrics.update(_summarize(label, restart_stats, restart_success))

	# SIMULATED ANNEALING VARIANTS
	for cooling, label, max_steps in (
		(1, "SimulatedAnnealingLinear", annealing_linear_max_steps),
		(2, "SimulatedAnnealingExponential", annealing_exp_max_steps),
	):
		annealing_stats: List[RunStats] = []
		annealing_success = 0

		for idx, board_seed in enumerate(base_boards):
			problem = EightQueensProblem()
			offset_key = "anneal_linear" if cooling == 1 else "anneal_exp"
			rng = random.Random(seed_offsets[offset_key] + idx)
			result, elapsed, memory_used, current_bytes, peak_bytes = measure_time_memory(
				simulated_annealing,
				problem,
				annealing_temperature,
				cooling,
				False,
				max_steps,
				initial_board=board_seed,
				rng=rng,
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
					extra={
						"temperature": float(annealing_temperature),
						"max steps": float(max_steps),
					},
				)
			)

		metrics.update(_summarize(label, annealing_stats, annealing_success))

	repo_root = Path(__file__).resolve().parents[2]
	output_dir = repo_root / "data" / "output" / "metrics"
	output_dir.mkdir(parents=True, exist_ok=True)
	metrics_path = output_dir / "metrics_hill_climbing.json"

	with metrics_path.open("w", encoding="utf-8") as fh:
		json.dump(metrics, fh, indent=4, ensure_ascii=False)

	if plot_hill_climbing_metrics:
		try:
			plot_hill_climbing_metrics(metrics, out_dir=repo_root / "data" / "output" / "graphics")
		except Exception:
			pass

	return metrics



__all__ = ["compare_hill_climbing_algorithms"]
