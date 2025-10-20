from typing import List, Tuple, Dict

# READS A MATRIX FROM A TEXT FILE AND RETURNS IT AS A LIST OF LISTS
def read_matrix_from_file(file_path: str) -> List[List[str]]:
    with open(file_path, "r") as f:
        lines = [line.rstrip("\n") for line in f.readlines() if line.strip() != ""]
    matrix = [list(line) for line in lines]
    return matrix


# GENERATES A GRAPH FROM A MATRIX USING 4-DIRECTIONAL MOVEMENT
def generate_graph_from_matrix(matrix: List[List[str]]) -> Dict[Tuple[int, int], list]:
    walkable = {".", "S", "G"}
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    graph = {}

    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] in walkable:
                neighbors = []
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and matrix[ni][nj] in walkable:
                        neighbors.append((ni, nj))
                graph[(i, j)] = neighbors

    return graph
