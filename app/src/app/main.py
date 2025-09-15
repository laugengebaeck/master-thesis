import cv2
import numpy as np
from networkx_importer import NetworkxImporter
from plans.load import load_plans
from plans.read import PlanReaderType
from tables.crop import pdf_convert_to_images
from topology_plans.find_lines import detect_lines, visualize_lines
from topology_plans.find_switches import (
    detect_triangles,
    get_triangle_center_points,
    visualize_switches,
)
from topology_plans.topology_graph import check_created_graph, create_graph, visualize_graph
from util import pillow_image_to_bytes


def table_main():
    zip_file = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"
    # export_plan_name = None
    export_plan_name = "P-Hausen"
    load_plans(zip_file, PlanReaderType.IMAGE_OPTIMIZED, export_plan_name)


def topology_main():
    # load PDF
    with open("../../Planungen_PT1/Forchheim_Ausschnitt_scanned.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        page_image = pillow_image_to_bytes(pdf_convert_to_images(pdf_bytes)[0])
        page_np = np.frombuffer(page_image, dtype=np.uint8)
        src = cv2.imdecode(page_np, cv2.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print("Error opening image!")
        return -1

    lines = detect_lines(src)
    visualize_lines(src, lines, "detected_probabilistic.png")

    topology = create_graph(lines)
    visualize_graph(src, topology, "topology_graph_overlay.png")

    triangles = detect_triangles(src)
    visualize_switches(src, triangles, "detected_triangles.png")

    check_created_graph(topology, get_triangle_center_points(triangles))

    yaramo = NetworkxImporter(topology).run()
    with open("yaramo_topology.json", "w") as file:
        file.write(yaramo.to_json())


if __name__ == "__main__":
    topology_main()
