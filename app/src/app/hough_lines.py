import cv2
import numpy as np
from zipfile import ZipFile

from util import pillow_image_to_bytes
from tables.table_crop import pdf_convert_to_images
from topology_plans.find_lines import detect_lines, visualize_lines
from topology_plans.find_switches import detect_triangles

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
    
    lines = detect_lines(src)
    visualize_lines(src, lines, "./detected_probabilistic.jpg")

    # detect_triangles(src)

if __name__ == "__main__":
    main()
