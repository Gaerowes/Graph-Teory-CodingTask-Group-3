"""Map selected points to the directed road graph and build a distance matrix."""
import math
import networkx as nx
import osmnx as ox


def snap_points_to_nodes(graph, points):
    """
    points is a list of dicts with name, lat, lon.
    Returns nearest graph node for each point.
    """
    node_ids = []
    for point in points:
        node = ox.distance.nearest_nodes(
            graph, X=float(point["lon"]), Y=float(point["lat"])
        )
        node_ids.append(node)
    return node_ids


def _shortest_path(graph, source, target, weight="length"):
    try:
        return nx.shortest_path(graph, source, target, weight=weight, method="dijkstra")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def _path_length(graph, path, weight="length"):
    """Sum minimum parallel-edge weight for each directed step in a MultiDiGraph."""
    if path is None:
        return math.inf
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v)
        if not edge_data:
            return math.inf
        edge_cost = min(
            float(data.get(weight, 1.0)) for data in edge_data.values()
        )
        total += edge_cost
    return total


def build_distance_matrix(graph, node_ids):
    """
    Build directed shortest-path distance matrix and save one shortest path per leg.
    Matrix entry [i][j] can differ from [j][i].
    """
    n = len(node_ids)
    matrix = [[math.inf] * n for _ in range(n)]
    paths = {}

    for i, source in enumerate(node_ids):
        matrix[i][i] = 0.0
        # Single-source Dijkstra is efficient for all destinations from this source.
        distances, predecessor = nx.single_source_dijkstra(
            graph, source, weight="length"
        )
        for j, target in enumerate(node_ids):
            if target not in distances:
                continue
            matrix[i][j] = float(distances[target])
            try:
                paths[(i, j)] = nx.shortest_path(
                    graph, source, target, weight="length", method="dijkstra"
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                paths[(i, j)] = None

    return matrix, paths


def expand_tour_to_nodes(tour, leg_paths):
    """Expand TSP node order into original road-network node sequence."""
    if not tour:
        return []
    expanded = []
    cycle = tour + [tour[0]]
    for a, b in zip(cycle[:-1], cycle[1:]):
        path = leg_paths.get((a, b))
        if path is None:
            return None
        if expanded:
            expanded.extend(path[1:])
        else:
            expanded.extend(path)
    return expanded


def road_nodes_to_latlon(graph, node_sequence):
    """Convert road node IDs to (lat, lon) coordinates for map display."""
    return [
        (float(graph.nodes[node]["y"]), float(graph.nodes[node]["x"]))
        for node in node_sequence
    ]
