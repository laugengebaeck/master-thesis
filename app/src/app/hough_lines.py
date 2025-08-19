import math
import cv2
import numpy as np
from zipfile import ZipFile

from util import pillow_image_to_bytes
from tables.table_crop import pdf_convert_to_images

SIMILAR_LINE_DISTANCE = 125
SHORT_LINE_LENGTH = 750

def is_line_angle_correct(line):
    # check angle, special handling for lines nearly parallel to y axis
    # TODO broken at the moment
    delta_y1 = abs(line[3] - line[1])
    delta_x1 = abs(line[2] - line[0])
    reject = delta_x1 < 10 or (abs(delta_y1 / delta_x1) >= 0.05 and (abs(delta_y1 / delta_x1) < 0.95 or abs(delta_y1 / delta_x1) > 2))
    return not reject
    
def is_line_long(line):
    # long lines are probably actual edges
    line_length = math.dist((line[0], line[1]), (line[2], line[3]))
    return line_length >= SHORT_LINE_LENGTH

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
 
    # Copy edges to the images that will display the results in BGR
    cdstP = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    
    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 125, 45)
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]

            if not is_line_angle_correct(l):
                continue

            if not is_line_long(l):
                found_flag = False
                for j in range(0, len(linesP)):
                    if i == j:
                        continue
                    l_comp = linesP[j][0]
                    if is_line_similar(l, l_comp):
                        found_flag = True
                        break
                if found_flag:
                    continue

            print(f"({l[0]}, {l[1]}) -- ({l[2]}, {l[3]})")
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)

    cv2.imwrite("./detected_probabilistic.jpg", cdstP)

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

def detect_triangles(src: cv2.typing.MatLike):
    dst = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)

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
        if len(approx) == 3:
            coordinates.append([cnt])
            if triangle_area(approx) < 50:
                continue
            cv2.drawContours(dst, [approx], 0, (0, 0, 255), 3)

    cv2.imwrite("detected_triangles.png", dst)

def main():
    # load ZIP
    zip_file = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"
    with ZipFile(zip_file, "r") as zip:
        pdf_file = zip.read("2019-10-30_PT1_ÄM02/PHSUxx50-Bl2.pdf")
        page_image = pillow_image_to_bytes(pdf_convert_to_images(pdf_file)[0])
        page_np = np.frombuffer(page_image, dtype=np.uint8)
        src = cv2.imdecode(page_np, cv2.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        return -1
    
    detect_lines(src)

    # detect_triangles(src)

if __name__ == "__main__":
    main()
