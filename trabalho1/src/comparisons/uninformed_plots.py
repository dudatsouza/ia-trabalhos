# EXTERNAL IMPORTS
import json
from pathlib import Path
import matplotlib.pyplot as plt

# PLOT UNINFORMED METRICS (DIJKSTRA VS BIDIRECTIONAL)
def plot_uninformed_metrics(metrics: dict, out_dir: str | Path | None = None):
    # PLOT BASIC COMPARISONS (TIME, NODES, MEMORY, COST)
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    out_dir = repo_root / 'data' / 'output' / 'graphics' / 'uninformed'

    # PREPARE DATA
    dijkstra_time = float(metrics.get('Dijkstra avg time (ms)', 0))
    bid_time = float(metrics.get('Bidirectional avg time (ms)', 0))

    dijkstra_nodes = float(metrics.get('Dijkstra avg nodes', 0))
    bid_nodes = float(metrics.get('Bidirectional avg nodes', 0))

    dijkstra_mem = float(metrics.get('Dijkstra avg memory (B)', 0))
    bid_mem = float(metrics.get('Bidirectional avg memory (B)', 0))

    dijkstra_cost = float(metrics.get('Dijkstra avg cost', 0))
    bid_cost = float(metrics.get('Bidirectional avg cost', 0))

    dijkstra_current = float(metrics.get('Dijkstra avg current (KB)', 0))
    bid_current = float(metrics.get('Bidirectional avg current (KB)', 0))

    dijkstra_peak = float(metrics.get('Dijkstra avg peak (KB)', 0))
    bid_peak = float(metrics.get('Bidirectional avg peak (KB)', 0))

    # BAR CHART: AVERAGE TIME
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_time, bid_time])
    plt.ylabel('TIME (ms)')
    plt.title('UNINFORMED: AVERAGE TIME')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_time.png')
    else:
        plt.show()
    plt.close()

    # BAR CHART: AVERAGE NODES EXPANDED
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_nodes, bid_nodes])
    plt.ylabel('NODES EXPANDED (AVG)')
    plt.title('UNINFORMED: AVG NODES EXPANDED')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_nodes.png')
    else:
        plt.show()
    plt.close()

    # BAR CHART: AVERAGE MEMORY (KB)
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_mem / 1024, bid_mem / 1024])
    plt.ylabel('MEMORY (KB)')
    plt.title('UNINFORMED: AVG MEMORY (KB)')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_memory_kb.png')
    else:
        plt.show()
    plt.close()

    # BAR CHART: AVERAGE COST
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_cost, bid_cost])
    plt.ylabel('COST (AVG)')
    plt.title('UNINFORMED: AVG COST')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_cost.png')
    else:
        plt.show()
    plt.close()

    # BAR CHART: AVERAGE CURRENT
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_current, bid_current])
    plt.ylabel('CURRENT (KB)')
    plt.title('UNINFORMED: AVG CURRENT (KB)')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_current.png')
    else:
        plt.show()
    plt.close()

    # BAR CHART: AVERAGE PEAK
    plt.figure(figsize=(6, 4))
    plt.bar(['Dijkstra', 'Bidirectional'], [dijkstra_peak, bid_peak])
    plt.ylabel('PEAK (KB)')
    plt.title('UNINFORMED: AVG PEAK (KB)')
    plt.tight_layout()
    if out_dir:
        plt.savefig(out_dir / 'uninformed_avg_peak.png')
    else:
        plt.show()
    plt.close()

    plot_uninformed_time_memory(metrics)
 

# LINE GRAPH: TIME (X) VS MEMORY (Y) PER ALGORITHM
def plot_uninformed_time_memory(metrics: dict, out_dir: str | Path | None = None):
    # PLOT BASIC COMPARISONS (TIME, NODES, MEMORY, COST)
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    out_dir = repo_root / 'data' / 'output' / 'graphics' / 'uninformed'
    # PREPARE DATA
    algorithms = ['Dijkstra', 'Bidirectional']
    time_values = [
        float(metrics.get('Dijkstra avg time (ms)', 0)),
        float(metrics.get('Bidirectional avg time (ms)', 0))
    ]
    memory_values = [
        float(metrics.get('Dijkstra avg memory (B)', 0)) / 1024,  # convert to KB
        float(metrics.get('Bidirectional avg memory (B)', 0)) / 1024
    ]

    # PLOT CONFIG
    plt.figure(figsize=(7, 4))
    
    # Cada linha representa um algoritmo
    for i, algorithm in enumerate(algorithms):
        plt.plot(time_values[i], memory_values[i], marker='o', label=algorithm)
    
    plt.xlabel('TIME (ms)')
    plt.ylabel('MEMORY (KB)')
    plt.title('UNINFORMED: TIME vs MEMORY')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # SAVE OR SHOW
    if out_dir:
        plt.savefig(out_dir / 'uninformed_time_vs_memory_line.png')
    else:
        plt.show()
    plt.close()



# SAVE/LOAD EXAMPLE UTIL (OPTIONAL)
def load_metrics_from_json(path: str | Path) -> dict:
    # LOAD METRICS DICTIONARY FROM JSON FILE
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    current_file = Path(__file__).resolve()
    repo_root = current_file.parents[2]
    
    example_path = repo_root / 'data' / 'output' / 'metrics' / 'metrics_uninformed.json'    
    
    if example_path.exists():
        metrics = load_metrics_from_json(example_path)
        plot_uninformed_metrics(metrics)
    else:
        print("EXAMPLE METRICS JSON NOT FOUND:", example_path)
