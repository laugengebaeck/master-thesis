import cv2
import numpy as np
from networkx_importer import NetworkxImporter
from plans.load import load_plans
from plans.read import PlanReaderType
from topology_plans.find_lines import detect_lines
from topology_plans.find_switches import detect_triangles
from topology_plans.thresholds import TopologyThresholds
from topology_plans.topology_graph import create_graph
from topology_plans.visualization import visualize_graph, visualize_lines, visualize_switches
from util import convert_pdf_to_images, pillow_image_to_bytes


def table_main():
    zip_file = "../../Planungen_PT1/2019-10-30_PT1_ÄM02.zip"
    # export_plan_name = None
    export_plan_name = "P-Hausen"
    load_plans(zip_file, PlanReaderType.IMAGE_OPTIMIZED, export_plan_name)


def topology_main():
    # load PDF
    is_pdf = True
    path_phausen = "../../Planungen_PT1/2019-10-30_PT1_ÄM02/PHSUxx50-Bl2.pdf"
    path_forchheim = "../../Planungen_PT1/Forchheim_Ausschnitt_scanned.pdf"
    path_forchheim_full = "../../Planungen_PT1/Forchheim_PT1_scanned.pdf"
    path_maschek = "../../Planungen_PT1/Maschek_Bild_10-7.png"
    path_pachl = "../../Planungen_PT1/Pachl_Bild_4-16.png"

    if is_pdf:
        with open(path_forchheim_full, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            page_image = pillow_image_to_bytes(convert_pdf_to_images(pdf_bytes)[0])
            page_np = np.frombuffer(page_image, dtype=np.uint8)
            src = cv2.imdecode(page_np, cv2.IMREAD_GRAYSCALE)
    else:
        src = cv2.imread(path_pachl, cv2.IMREAD_GRAYSCALE)

    # Check if image is loaded fine
    if src is None:
        print("Error opening image!")
        return -1

    thresholds = TopologyThresholds(*src.shape)

    lines = detect_lines(src, thresholds)
    visualize_lines(src, lines, "detected_probabilistic.png")

    topology = create_graph(lines, thresholds)
    visualize_graph(src, topology, "topology_graph_overlay.png")

    triangles = detect_triangles(src, thresholds)
    visualize_switches(src, triangles, "detected_triangles.png")

    # check_created_graph(topology, get_triangle_center_points(triangles), thresholds)

    yaramo = NetworkxImporter(topology).run()
    with open("export/yaramo_topology.json", "w") as file:
        file.write(yaramo.to_json())


if __name__ == "__main__":
    topology_main()
