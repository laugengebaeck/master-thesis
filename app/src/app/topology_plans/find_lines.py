import math
import cv2
import numpy as np

from topology_plans.vector import Vector2D

SIMILAR_LINE_DISTANCE = 150

def distance(point0: Vector2D, point1: Vector2D) -> float:
    return math.dist(point0.to_tuple(), point1.to_tuple())

def is_line_angle_correct(line: tuple[Vector2D, Vector2D]) -> bool:
    # check angle, special handling for lines nearly parallel to y axis
    delta_y1 = abs(line[1].y - line[0].y)
    delta_x1 = abs(line[1].x - line[0].x)
    angle = abs(math.degrees(math.atan(delta_y1/delta_x1))) if delta_x1 >= 10 else 90

    # we regard angles that differ by a multiple of 90 degrees as the same
    while round(angle) > 90:
        angle -= 90

    # reject 90 degrees angles, allow 0, ~20 and ~45 degree angles
    return angle == 0 or abs(angle - 20) < 10 or abs(angle - 45) < 10

# try removing signal symbol or text lines and similar
def is_line_similar(line: tuple[Vector2D, Vector2D], line_comp: tuple[Vector2D, Vector2D]) -> bool:
    # check if slopes are similar, else the lines are also not similar
    delta_y1 = abs(line[1].y - line[0].y)
    delta_x1 = abs(line[1].x - line[0].x)
    delta_y2 = abs(line_comp[1].y - line_comp[0].y)
    delta_x2 = abs(line_comp[1].x - line_comp[0].x)
    if delta_x1 != 0 and delta_x2 != 0 and abs(delta_y1 / delta_x1 - delta_y2 / delta_x2) > 0.5:
        return False
    
    # there are usually lots of lines near each other at these symbols
    startdist = distance(line[0], line_comp[0])
    enddist = distance(line[1], line_comp[1])
    startdist_switched = distance(line[0], line_comp[1])
    enddist_switched = distance(line[1], line_comp[0])

    # very complicated implementation of "both lines go in the same direction on the x-axis from the point where they meet"
    if startdist <= SIMILAR_LINE_DISTANCE:
        return (line[0].x < line[1].x) == (line_comp[0].x < line_comp[1].x)
    elif enddist <= SIMILAR_LINE_DISTANCE:
        return (line[1].x < line[0].x) == (line_comp[1].x < line_comp[0].x)
    elif startdist_switched <= SIMILAR_LINE_DISTANCE:
        return (line[0].x < line[1].x) == (line_comp[1].x < line_comp[0].x)
    elif enddist_switched <= SIMILAR_LINE_DISTANCE:
        return (line[1].x < line[0].x) == (line_comp[0].x < line_comp[1].x)
    
    return False
    
def convert_opencv_line_to_points(line) -> tuple[Vector2D, Vector2D]:
    line = line[0]
    return Vector2D(line[0], line[1]), Vector2D(line[2], line[3])
    
def detect_lines(src: cv2.typing.MatLike) -> list[tuple[Vector2D, Vector2D]]:
    dst = cv2.Canny(src, 50, 200, None, 3)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 125, 40)
    filtered_lines = []
    
    if linesP is not None:
        linesP = list(filter(lambda l: is_line_angle_correct(l) and distance(l[0], l[1]) >= 400, map(convert_opencv_line_to_points, linesP)))
        for l in linesP:
            found_flag = False
            for l_comp in linesP:
                # always keep the longest of the similar lines
                if is_line_similar(l, l_comp) and distance(l[0], l[1]) < distance(l_comp[0], l_comp[1]):
                    found_flag = True
                    break
            if not found_flag:
                filtered_lines.append(l)
        
    return filtered_lines

def visualize_lines(img, lines: list[tuple[Vector2D, Vector2D]], path):
    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for start, end in lines:
        cv2.line(color_dst, start.to_tuple(), end.to_tuple(), (0,0,255), 3, cv2.LINE_AA)
        # draw circles around the end points
        cv2.circle(color_dst, start.to_tuple(), 20, (0, 255, 0), 5)
        cv2.circle(color_dst, end.to_tuple(), 20, (0, 255, 0), 5)
        # debug thingy to print angles on the image
        cv2.putText(color_dst, f"{math.degrees(math.atan((end.y-start.y)/(end.x-start.x)))} deg", (int((start.x+end.x)//2), int((start.y+end.y)//2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)