import math

import cv2
import matplotlib.pyplot as plt
import networkx as nx
from topology_plans.vector import Vector2D


def visualize_lines(img: cv2.typing.MatLike, lines: list[tuple[Vector2D, Vector2D]], path: str):
    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for start, end in lines:
        cv2.line(color_dst, start.to_tuple(), end.to_tuple(), (0, 0, 255), 3, cv2.LINE_AA)
        # draw circles around the end points
        cv2.circle(color_dst, start.to_tuple(), 20, (0, 255, 0), 5)
        cv2.circle(color_dst, end.to_tuple(), 20, (0, 255, 0), 5)
        # debug thingy to print angles on the image
        cv2.putText(
            color_dst,
            f"{math.degrees(math.atan((end.y-start.y)/(end.x-start.x)))} deg",
            (int((start.x + end.x) // 2), int((start.y + end.y) // 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )
    cv2.imwrite(path, color_dst)


def visualize_graph(img: cv2.typing.MatLike, G: nx.Graph, path: str):
    nx.draw_planar(G, with_labels=True)
    plt.savefig("topology_graph.png")

    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for node in G.nodes:
        cv2.circle(color_dst, node, 20, (0, 255, 0), 5)
    for u, v in G.edges:
        cv2.line(color_dst, u, v, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)


def visualize_switches(img: cv2.typing.MatLike, switches: list[cv2.typing.MatLike], path: str):
    dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for switch in switches:
        cv2.drawContours(dst, [switch], 0, (0, 0, 255), 3)
    cv2.imwrite(path, dst)
