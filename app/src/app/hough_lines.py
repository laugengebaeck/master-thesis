import math
import cv2 as cv
import numpy as np
from zipfile import ZipFile

from util import pillow_image_to_bytes
from tables.table_crop import pdf_convert_to_images

SIMILAR_LINE_DISTANCE = 125
SHORT_LINE_LENGTH = 750

# try removing signal symbol or text lines and similar
def is_line_similar(line, line_comp):
    # we want to exclude long lines, they're probably actual edges
    line_length = math.dist((line[0], line[1]), (line[2], line[3]))
    if line_length >= SHORT_LINE_LENGTH:
        return False
    
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

def main():
    # load ZIP
    zip_file = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"
    with ZipFile(zip_file, "r") as zip:
        pdf_file = zip.read("2019-10-30_PT1_ÄM02/PHSUxx50-Bl2.pdf")
        page_image = pillow_image_to_bytes(pdf_convert_to_images(pdf_file)[0])
        page_np = np.frombuffer(page_image, dtype=np.uint8)
        src = cv.imdecode(page_np, cv.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        return -1

    dst = cv.Canny(src, 50, 200, None, 3)
 
    # Copy edges to the images that will display the results in BGR
    cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    
    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 125, 45)
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]

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
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

    cv.imwrite("./detected_probabilistic.jpg", cdstP)

if __name__ == "__main__":
    main()
