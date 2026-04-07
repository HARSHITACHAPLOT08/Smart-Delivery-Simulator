import networkx as nx
from typing import List, Optional, Tuple

from services.traffic import TrafficManager

def build_grid_graph(grid_size: int, traffic: Optional[TrafficManager] = None) -> nx.Graph:
    graph = nx.DiGraph()
    for x in range(grid_size):
        for y in range(grid_size):
            graph.add_node((x, y))
    for x in range(grid_size):
        for y in range(grid_size):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if 0 <= n[0] < grid_size and 0 <= n[1] < grid_size:
                    weight = traffic.edge_weight((x, y), n) if traffic else 1.0
                    graph.add_edge((x, y), n, weight=weight)
    return graph

def shortest_path(graph: nx.Graph, source: Tuple[int, int], target: Tuple[int, int]) -> List[Tuple[int, int]]:
    if source == target:
        return [source]
    try:
        return nx.astar_path(
            graph, source, target,
            heuristic=lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1]),
            weight="weight"
        )
    except nx.NetworkXNoPath:
        return [source]

def path_cost(graph: nx.Graph, path: List[Tuple[int, int]]) -> float:
    return sum(graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1)) if len(path) > 1 else 0.0
