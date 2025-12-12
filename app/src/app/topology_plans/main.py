import tomllib

from networkx_importer import NetworkxImporter
from planproexporter.generator import Generator as PlanProGenerator
from topology_plans.find_lines import detect_lines
from topology_plans.find_switches import detect_triangles
from topology_plans.line_segments import split_into_segments
from topology_plans.thresholds import TopologyThresholds
from topology_plans.topology_graph import create_graph
from topology_plans.validation.validator import TopologyValidator
from topology_plans.visualization import visualize_graph, visualize_lines, visualize_switches
from util.geometry import get_triangle_center_points
from util.images import load_img_from_path, remove_noise

long_paths = {
    "phausen": "../../Planungen_PT1/2019-10-30_PT1_ÄM02/PHSUxx50-Bl2.pdf",
    "forchheim_part": "../../Planungen_PT1/Forchheim_Ausschnitt_scanned.pdf",
    "forchheim_full": "../../Planungen_PT1/Forchheim_PT1_scanned.pdf",
    "ostelsheim": "../../Planungen_PT1/Ostelsheim_20250414.pdf",
}


def topology_main(path: str | None, path_slug: str | None):
    if path_slug is not None:
        path = long_paths[path_slug]
    if path is None:
        print("No input file given!")
        return -1

    src = load_img_from_path(path)
    if src is None:
        print("Could not open input file!")
        return -1
    src = remove_noise(src)

    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        config = data["tool"]["lst_plan_digi"]
        thresholds = TopologyThresholds(config, *src.shape)

    print("Detecting lines in the input document...")
    lines = detect_lines(src, thresholds)
    lines = split_into_segments(lines)
    visualize_lines(src, lines, "detected_probabilistic.png")

    print("Combining lines into a topology...")
    topology = create_graph(lines, thresholds)
    visualize_graph(src, topology, "topology_graph_overlay.png")

    print("Detecting switch symbols...")
    triangles = detect_triangles(src, thresholds)
    visualize_switches(src, triangles, "detected_triangles.png")

    print("Validating generated topology...")
    validator = TopologyValidator(thresholds)
    validation_failed = validator.check(topology, get_triangle_center_points(triangles))

    if validation_failed:
        print("Generated topology contains errors, cannot continue.")
        return -1

    print("Importing topology into Yaramo model...")
    try:
        yaramo = NetworkxImporter(topology).run()
        with open("export/yaramo_topology.json", "w") as file:
            file.write(yaramo.to_json())
        PlanProGenerator().generate(yaramo, filename="export/planpro_export")
    except Exception as e:
        print(
            "Yaramo import or PlanPro export did not complete successfully. Please re-check the generated topology for problems."
        )
        print(f"Exception message: {e}")
