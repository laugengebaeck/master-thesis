import math
import cv2
import numpy as np

SIMILAR_LINE_DISTANCE = 125

def line_length(line):
    return math.dist((line[0], line[1]), (line[2], line[3]))

def is_line_angle_correct(line):
    # check angle, special handling for lines nearly parallel to y axis
    delta_y1 = abs(line[3] - line[1])
    delta_x1 = abs(line[2] - line[0])
    angle = abs(math.degrees(math.atan(delta_y1/delta_x1))) if delta_x1 >= 10 else 90

    # we regard angles that differ by a multiple of 90 degrees as the same
    while round(angle) > 90:
        angle -= 90

    # reject 90 degrees angles, allow 0, ~20 and ~45 degree angles
    return angle == 0 or abs(angle - 20) < 10 or abs(angle - 45) < 10

# try removing signal symbol or text lines and similar
def is_line_similar(line, line_comp):
    # check if slopes are similar, else the lines are also not similar
    delta_y1 = abs(line[3] - line[1])
    delta_x1 = abs(line[2] - line[0])
    delta_y2 = abs(line_comp[3] - line_comp[1])
    delta_x2 = abs(line_comp[2] - line_comp[0])
    if delta_x1 != 0 and delta_x2 != 0 and abs(delta_y1 / delta_x1 - delta_y2 / delta_x2) > 2:
        return False
    
    # there are usually lots of lines near each other at these symbols
    startdist = math.dist((line[0], line[1]), (line_comp[0], line_comp[1]))
    enddist = math.dist((line[2], line[3]), (line_comp[2], line_comp[3]))
    startdist_switched = math.dist((line[0], line[1]), (line_comp[2], line_comp[3]))
    enddist_switched = math.dist((line[2], line[3]), (line_comp[0], line_comp[1]))
    if startdist <= SIMILAR_LINE_DISTANCE and enddist <= SIMILAR_LINE_DISTANCE:
        return True
    elif startdist_switched <= SIMILAR_LINE_DISTANCE and enddist_switched <= SIMILAR_LINE_DISTANCE:
        return True
    else:
        return False
    
def detect_lines(src: cv2.typing.MatLike):
    dst = cv2.Canny(src, 50, 200, None, 3)
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 125, 45)
    filtered_lines = []
    
    if linesP is not None:
        linesP = list(filter(lambda l: is_line_angle_correct(l), map(lambda l: l[0], linesP)))
        for l in linesP:
            found_flag = False
            for l_comp in linesP:
                # always keep the longest of the similar lines
                if is_line_similar(l, l_comp) and line_length(l) < line_length(l_comp):
                    found_flag = True
                    break
            if not found_flag:
                filtered_lines.append(l)
        
    return filtered_lines

def visualize_lines(img, lines, path):
    color_dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for l in lines:
        cv2.line(color_dst, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
        # debug thingy to print angles on the image
        cv2.putText(color_dst, f"{math.degrees(math.atan((l[3]-l[1])/(l[2]-l[0])))} deg", ((l[0]+l[2])//2, (l[1]+l[3])//2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imwrite(path, color_dst)