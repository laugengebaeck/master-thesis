import cv2
import math
import matplotlib.pyplot as plt
import networkx as nx

from util import flatten_iterable

SAME_NODE_DIST = 200

def create_graph(lines) -> nx.Graph:
    topology = nx.Graph()

    for line in lines:
        start = (line[0], line[1])
        end = (line[2], line[3])

        # find nearby nodes to join this line to
        # TODO also consider crossing points of lines for this
        if len(topology.nodes) > 0:
            start_closest = min(topology.nodes, key=lambda node: math.dist(start, node))
            if math.dist(start, start_closest) < SAME_NODE_DIST:
                start = start_closest
            end_closest = min(topology.nodes, key=lambda node: math.dist(end, node))
            if math.dist(end, end_closest) < SAME_NODE_DIST:
                end = end_closest
        
        topology.add_edge(start, end)

    larger_ccs = flatten_iterable(filter(lambda cc: len(cc) >= 5, nx.connected_components(topology)))
    topology = topology.subgraph(larger_ccs).copy()
    # topology = contract_paths(topology)
    nx.draw(topology)
    plt.savefig("topology_graph.png")
    return topology

def contract_paths(G: nx.Graph) -> nx.Graph:
    # TODO only allow contraction if node and both neighbors are on a straight line?
    for node in G.nodes:
        if len(G.edges(node)) == 2:
            for (u, v) in G.edges(node):
                if u == node:
                    G = nx.contracted_edge(G, (v, u), self_loops=False)
                else: 
                    G = nx.contracted_edge(G, (u, v), self_loops=False)
                break # We only want the first edge. Ugly solution, but better than nothing.
    return G

def visualize_graph(img: cv2.typing.MatLike, G: nx.Graph, path: str):
    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for node in G.nodes:
        cv2.circle(color_dst, node, 20, (0, 255, 0), 5)
    for (u, v) in G.edges:
        cv2.line(color_dst, u, v, (0,0,255), 3, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)