import math

import cv2
import numpy as np
from topology_plans.thresholds import TopologyThresholds
from util.vector import Vector2D


def is_line_angle_correct(line: tuple[Vector2D, Vector2D]) -> bool:
    # check angle, special handling for lines nearly parallel to y axis
    delta_y1 = abs(line[1].y - line[0].y)
    delta_x1 = abs(line[1].x - line[0].x)
    angle = abs(math.degrees(math.atan(delta_y1 / delta_x1))) if delta_x1 >= 10 else 90

    # reject 90 degree angles, allow 0, ~20 and ~45 degree angles
    return angle == 0 or abs(angle - 20) < 10 or abs(angle - 45) < 10


# try removing signal symbol or text lines and similar
def is_line_similar(
    line: tuple[Vector2D, Vector2D], line_comp: tuple[Vector2D, Vector2D], similar_line_dist: int
) -> bool:
    # check if slopes are similar, else the lines are also not similar
    delta_y1 = abs(line[1].y - line[0].y)
    delta_x1 = abs(line[1].x - line[0].x)
    delta_y2 = abs(line_comp[1].y - line_comp[0].y)
    delta_x2 = abs(line_comp[1].x - line_comp[0].x)
    if delta_x1 != 0 and delta_x2 != 0 and abs(delta_y1 / delta_x1 - delta_y2 / delta_x2) > 0.5:
        return False

    # there are usually lots of lines near each other at these symbols
    startdist = line[0].dist(line_comp[0])
    enddist = line[1].dist(line_comp[1])
    startdist_switched = line[0].dist(line_comp[1])
    enddist_switched = line[1].dist(line_comp[0])

    # do both lines go in the same direction on the x-axis from the point where they meet?
    if startdist <= similar_line_dist:
        return (line[0].x < line[1].x) == (line_comp[0].x < line_comp[1].x)
    elif enddist <= similar_line_dist:
        return (line[1].x < line[0].x) == (line_comp[1].x < line_comp[0].x)
    elif startdist_switched <= similar_line_dist:
        return (line[0].x < line[1].x) == (line_comp[1].x < line_comp[0].x)
    elif enddist_switched <= similar_line_dist:
        return (line[1].x < line[0].x) == (line_comp[0].x < line_comp[1].x)

    return False


def convert_opencv_line_to_points(line) -> tuple[Vector2D, Vector2D]:
    return Vector2D(line[0][0], line[0][1]), Vector2D(line[0][2], line[0][3])


def detect_lines(
    src: cv2.typing.MatLike, thresholds: TopologyThresholds
) -> list[tuple[Vector2D, Vector2D]]:
    dst = cv2.Canny(src, 50, 200, None, 3)
    linesP = cv2.HoughLinesP(
        dst, 1, np.pi / 180, 50, None, thresholds.min_line_length(), thresholds.max_line_gap()
    )
    filtered_lines = []

    if linesP is not None:
        linesP = list(
            filter(
                lambda l: is_line_angle_correct(l),
                map(convert_opencv_line_to_points, linesP),
            )
        )
        for l in linesP:
            found_flag = False
            for l_comp in linesP:
                # always keep the longest of the similar lines
                if is_line_similar(l, l_comp, thresholds.similar_line_distance()) and l[0].dist(
                    l[1]
                ) < l_comp[0].dist(l_comp[1]):
                    found_flag = True
                    break
            if not found_flag:
                filtered_lines.append(l)

    return filtered_lines
