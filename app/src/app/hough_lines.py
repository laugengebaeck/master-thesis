import sys
import math
from zipfile import ZipFile
import cv2 as cv
import numpy as np

from util import pillow_image_to_bytes
from tables.table_crop import pdf_convert_to_images


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
    cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)

    lines = cv.HoughLines(dst, 1, np.pi / 180, 200, None, 0, 0)
    
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            cv.line(cdst, pt1, pt2, (0,0,255), 3, cv.LINE_AA) 
    
    linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 20, 10)
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

    cv.imwrite("./detected_standard.jpg", cdst)
    cv.imwrite("./detected_probabilistic.jpg", cdstP)
    return 0

if __name__ == "__main__":
    main()
