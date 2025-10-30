from util.geometry import line_intersection
from util.vector import Vector2D


# split lines into segments intersecting only at end points to facilitate graph creation
def split_into_segments(lines: list[tuple[Vector2D, Vector2D]]) -> list[tuple[Vector2D, Vector2D]]:
    finished_lines = []
    lines_to_process = lines

    while len(lines_to_process) > 0:
        found_intersection = False
        edge = lines_to_process.pop(0)
        # finished_lines have no relevant intersections anymore, so no need to check them here
        for other_edge in lines_to_process:
            intersection = line_intersection(edge, other_edge)
            # if intersection exists and is not one of the end points, split both edges
            if (
                intersection is not None
                and intersection != edge[0]
                and intersection != edge[1]
                and intersection != other_edge[0]
                and intersection != other_edge[1]
            ):
                found_intersection = True
                lines_to_process.remove(other_edge)
                lines_to_process.extend(
                    [
                        (edge[0], intersection),
                        (intersection, edge[1]),
                        (other_edge[0], intersection),
                        (intersection, other_edge[1]),
                    ]
                )
                break
        if not found_intersection:
            finished_lines.append(edge)

    return finished_lines
