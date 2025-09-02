import math
import cv2
import numpy as np

def triangle_area(approx: cv2.typing.MatLike):
    pnt0 = approx[0][0]
    pnt1 = approx[1][0]
    pnt2 = approx[2][0]
    a = math.dist(pnt0, pnt1)
    b = math.dist(pnt1, pnt2)
    c = math.dist(pnt2, pnt0)
    s = (a + b + c) / 2

    # Heron's formula
    return math.sqrt(s * (s - a) * (s - b) * (s - c))

# see https://stackoverflow.com/questions/60964249/how-to-check-the-color-of-pixels-inside-a-polygon-and-remove-the-polygon-if-it-c
# counts number of white pixels
def is_black_inside(img: cv2.typing.MatLike, triangle: cv2.typing.MatLike):
    points = np.asarray(triangle[:,:])
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, [points], (255))
    values = img[np.where(mask == 255)]
    count = 0
    for value in values:
        if value == 255:
            count += 1
    return count <= 5

def detect_triangles(src: cv2.typing.MatLike):
    kernel = np.ones((4, 4), np.uint8)
    dilation = cv2.dilate(src, kernel, iterations=1)
    blur = cv2.GaussianBlur(dilation, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    coordinates = []
    for cnt in contours:
        approx = cv2.approxPolyDP(
            cnt, 0.07 * cv2.arcLength(cnt, True), True)
        if len(approx) == 3 and triangle_area(approx) >= 50 and triangle_area(approx) <= 500 and is_black_inside(src, approx):
            coordinates.append(approx)
    return coordinates

def visualize_switches(img, switches, path):
    dst = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for switch in switches:
        cv2.drawContours(dst, [switch], 0, (0, 0, 255), 3)
    cv2.imwrite(path, dst)