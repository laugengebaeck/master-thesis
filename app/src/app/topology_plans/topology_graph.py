import math
import matplotlib.pyplot as plt
import networkx as nx

SAME_NODE_DIST = 5

def create_graph(lines):
    topology = nx.Graph()
    for line in lines:
        start = (line[0], line[1])
        end = (line[2], line[3])
        # find adjacent nodes to join this line to
        for node in topology.nodes:
            if math.dist(start, node) < SAME_NODE_DIST:
                start = node
            elif math.dist(end, node):
                end = node
        topology.add_edge(start, end)
    largest_cc = max(nx.connected_components(topology), key=len)
    topology = topology.subgraph(largest_cc).copy()
    topology = contract_paths(topology)
    # TODO plot stuff on the plan instead to better see what this is doing
    nx.draw(topology)
    plt.savefig("topology_graph.png")

def contract_paths(G: nx.Graph) -> nx.Graph:
    for node in G.nodes:
        if len(G.edges(node)) == 1 or len(G.edges(node)) == 2:
            for (u, v) in G.edges(node):
                G = nx.contracted_edge(G, (v, u), self_loops=False)
                break # We only want the first edge. Ugly solution, but better than nothing.
    return G