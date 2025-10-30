import math

import cv2
import numpy as np
import shapely
from util.vector import Vector2D


# measures distance between point p and line segment vw
# https://stackoverflow.com/a/1501725
def dist_point_line_segment(p: Vector2D, line_segment: tuple[Vector2D, Vector2D]) -> float:
    v, w = line_segment
    l_vw_squared = (v.x - w.x) ** 2 + (v.y - w.y) ** 2
    if l_vw_squared == 0:
        return p.dist(v)

    # Consider the line extending the segment, parameterized as v + t (w - v).
    # We find projection of point p onto the line.
    # It falls where t = [(p-v) . (w-v)] / |w-v|^2
    # We clamp t from [0,1] to handle points outside the segment vw.
    t = max(0, min(1, float((p - v).dot(w - v) / l_vw_squared)))
    projection = v + t * (w - v)

    # Projection falls on the segment
    return p.dist(projection)


def line_intersection(
    line1: tuple[Vector2D, Vector2D], line2: tuple[Vector2D, Vector2D]
) -> Vector2D | None:
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


def triangle_to_points(triangle: cv2.typing.MatLike):
    return triangle[0][0], triangle[1][0], triangle[2][0]


def triangle_area(approx: cv2.typing.MatLike):
    pnt0, pnt1, pnt2 = triangle_to_points(approx)
    a = math.dist(pnt0, pnt1)
    b = math.dist(pnt1, pnt2)
    c = math.dist(pnt2, pnt0)
    s = (a + b + c) / 2

    # Heron's formula
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def get_triangle_center_points(coordinates) -> list[Vector2D]:
    centers = []
    for approx in coordinates:
        pnt0, pnt1, pnt2 = triangle_to_points(approx)
        x_middle = (pnt0[0] + pnt1[0] + pnt2[0]) // 3
        y_middle = (pnt0[1] + pnt1[1] + pnt2[1]) // 3
        centers.append(Vector2D.from_tuple((x_middle, y_middle)))
    return centers
