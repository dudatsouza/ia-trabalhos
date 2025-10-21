# EXTERNAL IMPORTS
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# INTERNAL PROJECT IMPORTS
# NONE FOR THIS EXAMPLE (ADD YOUR PROJECT IMPORTS IF NEEDED)


# PLOT INFORMED METRICS (A* VS GREEDY FOR MULTIPLE HEURISTICS)
def plot_informed_metrics(metrics: dict, heuristics: list | None = None, out_dir: str | Path | None = None):
    # PLOT MULTI-HEURISTIC COMPARISONS (TIME, NODES, COST) FOR A* AND GREEDY
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    out_dir = repo_root / 'data' / 'output' / 'graphics' / 'informed'

    # DEFAULT HEURISTICS IF NOT PROVIDED
    heuristics = heuristics or ['Manhattan', 'Euclidean', 'Inadmissible']

    # EXTRACT PER-HEURISTIC METRICS
    times_astar = []
    times_greedy = []
    nodes_astar = []
    nodes_greedy = []
    costs_astar = []
    costs_greedy = []
    peaks_astar = []
    peaks_greedy = []
    memorys_astar = []
    memorys_greedy = []
    currents_astar = []
    currents_greedy = []

    for h in heuristics:
        key_astar_time = f"A*-{h} avg time (ms)"
        key_greedy_time = f"Greedy-{h} avg time (ms)"
        times_astar.append(float(metrics.get(key_astar_time, 0)))
        times_greedy.append(float(metrics.get(key_greedy_time, 0)))

        key_astar_nodes = f"A*-{h} avg nodes"
        key_greedy_nodes = f"Greedy-{h} avg nodes"
        nodes_astar.append(float(metrics.get(key_astar_nodes, 0)))
        nodes_greedy.append(float(metrics.get(key_greedy_nodes, 0)))

        key_astar_cost = f"A*-{h} avg cost"
        key_greedy_cost = f"Greedy-{h} avg cost"
        costs_astar.append(float(metrics.get(key_astar_cost, 0)))
        costs_greedy.append(float(metrics.get(key_greedy_cost, 0)))

        key_astar_peak = f"A*-{h} avg peak (KB)"
        key_greedy_peak = f"Greedy-{h} avg peak (KB)"
        peaks_astar.append(float(metrics.get(key_astar_peak, 0)))
        peaks_greedy.append(float(metrics.get(key_greedy_peak, 0)))

        key_astar_memory = f"A*-{h} avg memory (B)"
        key_greedy_memory = f"Greedy-{h} avg memory (B)"
        memorys_astar.append(float(metrics.get(key_astar_memory, 0)))
        memorys_greedy.append(float(metrics.get(key_greedy_memory, 0)))

        key_astar_current = f"A*-{h} avg current (KB)"
        key_greedy_current = f"Greedy-{h} avg current (KB)"
        currents_astar.append(float(metrics.get(key_astar_current, 0)))
        currents_greedy.append(float(metrics.get(key_greedy_current, 0)))

    x = np.arange(len(heuristics))
    width = 0.35

    # GROUPED BAR: TIME
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, times_astar, width, label='A*')
    plt.bar(x + width/2, times_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('TIME (ms)')
    plt.title('INFORMED: AVG TIME BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_time_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    # GROUPED BAR: NODES
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, nodes_astar, width, label='A*')
    plt.bar(x + width/2, nodes_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('NODES EXPANDED (AVG)')
    plt.title('INFORMED: AVG NODES BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_nodes_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    # GROUPED BAR: COST
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, costs_astar, width, label='A*')
    plt.bar(x + width/2, costs_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('PATH COST (AVG)')
    plt.title('INFORMED: AVG COST BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_cost_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    # GROUPED BAR: PEAK
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, peaks_astar, width, label='A*')
    plt.bar(x + width/2, peaks_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('PATH PEAK (KB)')
    plt.title('INFORMED: AVG PEAK (KB) BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_peak_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    # GROUPED BAR: MEMORY
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, memorys_astar, width, label='A*')
    plt.bar(x + width/2, memorys_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('PATH MEMORY (B)')
    plt.title('INFORMED: MEMORY (B) BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_memory_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    # GROUPED BAR: CURRENT
    plt.figure(figsize=(8, 4))
    plt.bar(x - width/2, currents_astar, width, label='A*')
    plt.bar(x + width/2, currents_greedy, width, label='Greedy')
    plt.xticks(x, heuristics)
    plt.ylabel('PATH CURRENT (KB)')
    plt.title('INFORMED: CURRENT (KB) BY HEURISTIC')
    plt.legend()
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'informed_avg_current_by_heuristic.png')
    else:
        plt.show()
    plt.close()

    plot_informed_time_memory(metrics)


# LINE GRAPH: TIME (X) VS MEMORY (Y) FOR INFORMED SEARCHES
def plot_informed_time_memory(metrics: dict, out_dir: str | Path | None = None):
    # PLOT MULTI-HEURISTIC COMPARISONS (TIME, NODES, COST) FOR A* AND GREEDY
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    out_dir = repo_root / 'data' / 'output' / 'graphics' / 'informed'

    # DEFINE ALGORITHMS AND HEURISTICS (ALL 4 HEURISTICS)
    algorithms = [
        ('A*-Manhattan',   metrics.get('A*-Manhattan avg time (ms)', 0),   metrics.get('A*-Manhattan avg peak (KB)', 0)),
        ('A*-Euclidean',   metrics.get('A*-Euclidean avg time (ms)', 0),   metrics.get('A*-Euclidean avg peak (KB)', 0)),
        ('A*-Inadmissible', metrics.get('A*-Inadmissible avg time (ms)', 0), metrics.get('A*-Inadmissible avg peak (KB)', 0)),

        ('Greedy-Manhattan', metrics.get('Greedy-Manhattan avg time (ms)', 0), metrics.get('Greedy-Manhattan avg peak (KB)', 0)),
        ('Greedy-Euclidean', metrics.get('Greedy-Euclidean avg time (ms)', 0), metrics.get('Greedy-Euclidean avg peak (KB)', 0)),
        ('Greedy-Inadmissible', metrics.get('Greedy-Inadmissible avg time (ms)', 0), metrics.get('Greedy-Inadmissible avg peak (KB)', 0))
    ]

    # PREPARE PLOT
    plt.figure(figsize=(8, 5))
    
    for name, time_val, mem_val in algorithms:
        plt.plot(
            float(time_val),
            float(mem_val) / 1024,  # Convert B → KB
            marker='o',
            label=name
        )
    
    plt.xlabel('TIME (ms)')
    plt.ylabel('MEMORY (KB)')
    plt.title('INFORMED: TIME vs MEMORY')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # SAVE OR SHOW
    if out_dir:
        plt.savefig(out_dir / 'informed_time_vs_memory_line.png')
    else:
        plt.show()
    plt.close()



# SAVE/LOAD EXAMPLE UTIL (OPTIONAL)
def load_metrics_from_json(path: str | Path) -> dict:
    # LOAD METRICS DICTIONARY FROM JSON FILE
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    # SIMPLE CLI EXAMPLE: LOAD EXAMPLE JSON AND PLOT
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    example_path = repo_root / 'data' / 'output' / 'metrics' / 'metrics_informed.json'    
    if example_path.exists():
        metrics = load_metrics_from_json(example_path)
        plot_informed_metrics(metrics)
    else:
        print("EXAMPLE METRICS JSON NOT FOUND:", example_path)
