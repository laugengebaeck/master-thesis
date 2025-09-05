import cv2
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from shapely.geometry import LineString

from util import flatten_iterable

SAME_NODE_DIST = 200
SPUR_MAX_LENGTH = 300

def line_intersection(line1, line2):
    u1, v1 = line1
    u2, v2 = line2
    ls1 = LineString([u1, v1])
    ls2 = LineString([u2, v2])
    if not ls1.intersects(ls2):
        return None
    intersection = ls1.intersection(ls2)
    return np.int32(intersection.x), np.int32(intersection.y) # type: ignore

# split lines into segments intersecting only at end points to facilitate graph creation
def split_into_segments(lines: list[tuple[tuple[np.int32, np.int32], tuple[np.int32, np.int32]]]) -> list[tuple[tuple[np.int32, np.int32], tuple[np.int32, np.int32]]]:
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


def create_graph(lines) -> nx.Graph:
    topology = nx.Graph()

    lines = list(map(lambda line: ((line[0], line[1]), (line[2], line[3])), lines))

    lines = split_into_segments(lines)

    for start, end in lines:
        # find nearby nodes to join this line to
        if len(topology.nodes) > 0:
            start_closest = min(topology.nodes, key=lambda node: math.dist(start, node))
            if math.dist(start, start_closest) <= SAME_NODE_DIST:
                start = start_closest
            end_closest = min(topology.nodes, key=lambda node: math.dist(end, node))
            if math.dist(end, end_closest) <= SAME_NODE_DIST:
                end = end_closest
        if start != end:
            topology.add_edge(start, end)

    # TODO find out what is going on with these weird triangles in the graph
    topology = remove_spurs(topology)
    largest_cc = max(nx.connected_components(topology), key=len)
    topology = topology.subgraph(largest_cc).copy()
    return topology

def remove_spurs(G: nx.Graph) -> nx.Graph:
    for u, v in G.edges:
        if math.dist(u, v) <= SPUR_MAX_LENGTH and (G.degree[u] == 1 or G.degree[v] == 1): # type: ignore
            G.remove_edge(u, v)
    return G

def contract_paths(G: nx.Graph) -> nx.Graph:
    # TODO make this work correctly before using it
    # TODO only allow contraction if node and both neighbors are on a straight line?
    for node in G.nodes:
        if G.degree[node] == 2: # type: ignore
            for u, v in G.edges(node):
                if u == node:
                    G = nx.contracted_edge(G, (v, u), self_loops=False)
                elif v == node: 
                    G = nx.contracted_edge(G, (u, v), self_loops=False)
                break # We only want the first edge. Ugly solution, but better than nothing.
    return G

def visualize_graph(img: cv2.typing.MatLike, G: nx.Graph, path: str):
    nx.draw(G)
    plt.savefig("topology_graph.png")

    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for node in G.nodes:
        cv2.circle(color_dst, node, 20, (0, 255, 0), 5)
    for (u, v) in G.edges:
        cv2.line(color_dst, u, v, (0,0,255), 3, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)