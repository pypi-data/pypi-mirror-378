import numpy as np

def find_connected_component(adj_matrix: np.ndarray) -> list:
    """
    Find connected components in an undirected graph represented by an adjacency matrix.
    
    :param adj_matrix: Adjacency matrix of the graph.
    :return: List of connected components, where each component is a list of node indices.
    """
    n = adj_matrix.shape[0]
    visited = np.zeros(n, dtype=bool)
    components = []

    def dfs(node: int, component: list):
        visited[node] = True
        component.append(node)
        for neighbor in range(n):
            if adj_matrix[node, neighbor] == 1 and not visited[neighbor]:
                dfs(neighbor, component)

    for i in range(n):
        if not visited[i]:
            component = []
            dfs(i, component)
            components.append(component)

    return components

chip_topology = np.eye(20, dtype=np.int8)
chip_topology[0, 1:20] = 1
chip_topology[1:20, 0] = 1

print("Chip topology:")
print(chip_topology)
print("Connected components:")
print(find_connected_component(chip_topology))