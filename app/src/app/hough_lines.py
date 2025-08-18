import math
import cv2 as cv
import numpy as np

from itertools import groupby
from zipfile import ZipFile

from util import pillow_image_to_bytes
from tables.table_crop import pdf_convert_to_images

SIMILAR_LINE_DISTANCE = 200

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

    # first sort by x coordinates, then by y coordinates
    linesP = sorted(linesP, key = lambda l: (l[0][0], l[0][2], l[0][1], l[0][3]))
    
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            lprev = linesP[i-1][0] if i > 0 else None
            # first sketchy try at removing signal symbol lines and similar
            # there are usually lots of lines near each other at these symbols
            # should also check if line lengths are small
            # should also do the same check with lnext
            if lprev is not None:
                startdist = math.dist((l[0], l[1]), (lprev[0], lprev[1]))
                enddist = math.dist((l[2], l[3]), (lprev[2], lprev[3]))
                startdist_switched = math.dist((l[0], l[1]), (lprev[2], lprev[3]))
                enddist_switched = math.dist((l[2], l[3]), (lprev[0], lprev[1]))
                if (startdist <= SIMILAR_LINE_DISTANCE and enddist <= SIMILAR_LINE_DISTANCE) or (startdist_switched <= SIMILAR_LINE_DISTANCE and enddist_switched <= SIMILAR_LINE_DISTANCE):
                    continue
            print(f"({l[0]}, {l[1]}) -- ({l[2]}, {l[3]})")
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

    # linesPGrouped = groupby(linesP, lambda l: round(l[0][1], -1))

    # groups = [{'type':k, 'items':[x[0] for x in v]} for k, v in linesPGrouped]

    #for group in groups:
    #    print(f"{group['type']} -> {group['items']}")

    cv.imwrite("./detected_probabilistic.jpg", cdstP)

if __name__ == "__main__":
    main()
