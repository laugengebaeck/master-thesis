import math

import networkx as nx
from topology_plans.thresholds import TopologyThresholds
from util.geometry import dist_point_line_segment
from util.vector import Vector2D


def remove_spurs(G: nx.Graph, max_spur_length: int) -> nx.Graph:
    for u, v in G.edges:
        if math.dist(u, v) <= max_spur_length and (G.degree[u] == 1 or G.degree[v] == 1):  # type: ignore
            G.remove_edge(u, v)
    return G


def remove_nodes_on_other_edges(G: nx.Graph, on_edge_dist: int) -> nx.Graph:
    # nodes of degree 1, that are on edges, but not the edge's endpoint, are an artifact and can just be deleted
    nodes_to_remove = []
    for node in G.nodes:
        if G.degree[node] == 1:  # type: ignore
            for edge in G.edges:
                distance = dist_point_line_segment(
                    Vector2D.from_tuple(node),
                    (Vector2D.from_tuple(edge[0]), Vector2D.from_tuple(edge[1])),
                )
                if (
                    node != edge[0]
                    and node != edge[1]
                    and edge[0] not in nodes_to_remove
                    and edge[1] not in nodes_to_remove
                    and distance <= on_edge_dist
                ):
                    nodes_to_remove.append(node)
                    break
    for node in nodes_to_remove:
        G.remove_node(node)
    return G


def create_graph(
    lines: list[tuple[Vector2D, Vector2D]], thresholds: TopologyThresholds
) -> nx.Graph:
    topology = nx.Graph()

    for start_pt, end_pt in lines:
        # find nearby nodes to join this line to
        start = start_pt.to_tuple()
        end = end_pt.to_tuple()
        if len(topology.nodes) > 0:
            start_closest = min(topology.nodes, key=lambda node: math.dist(start, node))
            if math.dist(start, start_closest) <= thresholds.same_node_distance():
                start = start_closest
            end_closest = min(topology.nodes, key=lambda node: math.dist(end, node))
            if math.dist(end, end_closest) <= thresholds.same_node_distance():
                end = end_closest
        if start != end:
            topology.add_edge(start, end)

    topology = remove_spurs(topology, thresholds.max_spur_length())
    topology = remove_nodes_on_other_edges(topology, thresholds.on_edge_dist())
    largest_cc = max(nx.connected_components(topology), key=len)
    topology = topology.subgraph(largest_cc).copy()
    return topology
