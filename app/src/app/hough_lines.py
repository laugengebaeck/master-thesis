import cv2
import numpy as np
from zipfile import ZipFile

from util import pillow_image_to_bytes
from tables.crop import pdf_convert_to_images
from topology_plans.find_lines import detect_lines, visualize_lines
from topology_plans.find_switches import detect_triangles, visualize_switches
from topology_plans.topology_graph import create_graph, visualize_graph

def main():
    # load PDF
    with open("../../Planungen_PT1/Forchheim_Ausschnitt_scanned.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        page_image = pillow_image_to_bytes(pdf_convert_to_images(pdf_bytes)[0])
        page_np = np.frombuffer(page_image, dtype=np.uint8)
        src = cv2.imdecode(page_np, cv2.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print ('Error opening image!')
        return -1
    
    lines = detect_lines(src)
    visualize_lines(src, lines, "detected_probabilistic.jpg")

    topology = create_graph(lines)
    visualize_graph(src, topology, "topology_graph_overlay.png")

    triangles = detect_triangles(src)
    visualize_switches(src, triangles, "detected_triangles.png")

if __name__ == "__main__":
    main()
