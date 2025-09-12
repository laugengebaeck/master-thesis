import cv2
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import shapely

from topology_plans.vector import Vector2D

SAME_NODE_DIST = 200
SPUR_MAX_LENGTH = 300

def dot(p1: Vector2D, p2: Vector2D) -> int:
    return int(p1.x * p2.x + p1.y * p2.y)

# measures distance between point p and line segment vw
# https://stackoverflow.com/a/1501725
def dist_point_line_segment(p: Vector2D, line_segment: tuple[Vector2D, Vector2D]) -> float:
    v, w = line_segment
    l_vw_squared = (v.x - w.x) ** 2 + (v.y - w.y) ** 2
    if l_vw_squared == 0: 
        return math.dist(p.to_tuple(), v.to_tuple())
    
    # Consider the line extending the segment, parameterized as v + t (w - v).
    # We find projection of point p onto the line. 
    # It falls where t = [(p-v) . (w-v)] / |w-v|^2
    # We clamp t from [0,1] to handle points outside the segment vw.
    t = max(0, min(1, float(dot(p - v, w - v) / l_vw_squared)));
    projection = v + t * (w - v);  # Projection falls on the segment
    return math.dist(p.to_tuple(), projection.to_tuple())

def line_intersection(line1: tuple[Vector2D, Vector2D], line2: tuple[Vector2D, Vector2D]) -> Vector2D | None:
    u1, v1 = line1
    u2, v2 = line2
    ls1 = shapely.geometry.LineString([u1.to_tuple(), v1.to_tuple()])
    ls2 = shapely.geometry.LineString([u2.to_tuple(), v2.to_tuple()])
    if not ls1.intersects(ls2):
        return None
    intersection = ls1.intersection(ls2)
    if isinstance(intersection, shapely.geometry.Point):
        return Vector2D(np.int32(intersection.x), np.int32(intersection.y))
    else:
        return None

# split lines into segments intersecting only at end points to facilitate graph creation
def split_into_segments(lines: list[tuple[Vector2D, Vector2D]]) -> list[tuple[Vector2D, Vector2D]]:
    finished_lines = []
    lines_to_process = lines

    while len(lines_to_process) > 0:
        found_intersection = False
        edge = lines_to_process.pop(0)
        # finished_lines have no relevant intersections anymore, so no need to check them here
        for other_edge in lines_to_process:
            intersection = line_intersection(edge, other_edge)
            # if intersection exists and is not one of the end points, split both edges
            if intersection is not None and intersection != edge[0] and intersection != edge[1] and intersection != other_edge[0] and intersection != other_edge[1]:
                found_intersection = True
                lines_to_process.remove(other_edge)
                lines_to_process.extend([(edge[0], intersection), (intersection, edge[1]), (other_edge[0], intersection), (intersection, other_edge[1])])
                break
        if not found_intersection:
            finished_lines.append(edge)

    return finished_lines


def create_graph(lines: list[tuple[Vector2D, Vector2D]]) -> nx.Graph:
    topology = nx.Graph()

    lines = split_into_segments(lines)

    for start_pt, end_pt in lines:
        # find nearby nodes to join this line to
        start = start_pt.to_tuple()
        end = end_pt.to_tuple()
        if len(topology.nodes) > 0:
            start_closest = min(topology.nodes, key=lambda node: math.dist(start, node))
            if math.dist(start, start_closest) <= SAME_NODE_DIST:
                start = start_closest
            end_closest = min(topology.nodes, key=lambda node: math.dist(end, node))
            if math.dist(end, end_closest) <= SAME_NODE_DIST:
                end = end_closest
        if start != end:
            topology.add_edge(start, end)

    topology = remove_spurs(topology)
    topology = remove_nodes_on_other_edges(topology)
    largest_cc = max(nx.connected_components(topology), key=len)
    topology = topology.subgraph(largest_cc).copy()
    topology = contract_paths(topology)
    return topology

def remove_spurs(G: nx.Graph) -> nx.Graph:
    for u, v in G.edges:
        if math.dist(u, v) <= SPUR_MAX_LENGTH and (G.degree[u] == 1 or G.degree[v] == 1): # type: ignore
            G.remove_edge(u, v)
    return G

def remove_nodes_on_other_edges(G: nx.Graph) -> nx.Graph:
    # nodes of degree 1, that are on edges, but not the edge's endpoint, are an artifact and can just be deleted
    nodes_to_remove = []
    for node in G.nodes:
        if G.degree[node] == 1: # type: ignore
            for edge in G.edges:
                distance = dist_point_line_segment(Vector2D.from_tuple(node), (Vector2D.from_tuple(edge[0]), Vector2D.from_tuple(edge[1])))
                if node != edge[0] and node != edge[1] and edge[0] not in nodes_to_remove and edge[1] not in nodes_to_remove and distance <= 5:
                    nodes_to_remove.append(node)
                    break
    for node in nodes_to_remove:
        G.remove_node(node)
    return G

def contract_paths(G: nx.Graph) -> nx.Graph:
    for node in G.nodes:
        if G.degree[node] == 2: # type: ignore
            (u, v), _ = G.edges(node) # only take the first edge
            # choose order so that correct node is deleted during contraction
            if u == node:
                G = nx.contracted_edge(G, (v, u), self_loops=False)
            elif v == node: 
                G = nx.contracted_edge(G, (u, v), self_loops=False)
    return G

def visualize_graph(img: cv2.typing.MatLike, G: nx.Graph, path: str):
    nx.draw_planar(G, with_labels=True)
    plt.savefig("topology_graph.png")

    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for node in G.nodes:
        cv2.circle(color_dst, node, 20, (0, 255, 0), 5)
    for (u, v) in G.edges:
        cv2.line(color_dst, u, v, (0,0,255), 3, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)

def check_created_graph(G: nx.Graph, detected_switch_positions: list[Vector2D]):
    for node in G.nodes:
        if G.degree[node] >= 4: # type: ignore
            print(f"In the created topology, node {node} has more than 3 neighbors. That's wrong.")
        if G.degree[node] == 3 and all(math.dist(node, switch.to_tuple()) > 200 for switch in detected_switch_positions): # type: ignore
            # TODO umgekehrt auch Dreieck, aber keine Weiche
            print(f"In the created topology, node {node} functions as a switch, but no switch symbol was found there. That's probably wrong.")
    cycles = sorted(nx.simple_cycles(G))
    if len(cycles) > 0:
        print(f"The created topology contains cycles. That's wrong.")
        print(f"Cycles: {cycles}")