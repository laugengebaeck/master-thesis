import cv2
import numpy as np
from topology_plans.thresholds import TopologyThresholds
from util.geometry import triangle_area


# see https://stackoverflow.com/questions/60964249/how-to-check-the-color-of-pixels-inside-a-polygon-and-remove-the-polygon-if-it-c
# counts number of white pixels
def is_black_inside(img: cv2.typing.MatLike, triangle: cv2.typing.MatLike):
    points = np.asarray(triangle[:, :])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, [points], (255))
    values = img[np.where(mask == 255)]
    count = 0
    for value in values:
        if value == 255:
            count += 1
    return count <= 5


# https://stackoverflow.com/questions/46300244/triangle-detection-using-opencv
def detect_triangles(src: cv2.typing.MatLike, thresholds: TopologyThresholds):
    min_switch_area, max_switch_area = thresholds.switch_area_bounds()

    thresh = cv2.adaptiveThreshold(
        src, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    coordinates = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.07 * cv2.arcLength(cnt, True), True)
        # TODO black condition is good for discarding incorrect triangles, but only works for "ferngestellte Weichen"
        if (
            len(approx) == 3
            and triangle_area(approx) >= min_switch_area
            and triangle_area(approx) <= max_switch_area
            and is_black_inside(src, approx)
        ):
            coordinates.append(approx)
    return coordinates
