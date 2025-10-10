class TopologyThresholds:
    def __init__(self, width: int, height: int) -> None:
        self.scale_factor = min(width, height)

    def similar_line_distance(self) -> int:
        return round(0.06 * self.scale_factor)

    def min_line_length(self) -> int:
        return round(0.06 * self.scale_factor)

    def max_line_gap(self) -> int:
        return round(0.015 * self.scale_factor)

    def same_node_distance(self) -> int:
        return round(0.07 * self.scale_factor)

    def max_spur_length(self) -> int:
        return round(0.075 * self.scale_factor)

    def on_edge_dist(self) -> int:
        return round(0.00125 * self.scale_factor)

    def switch_area_bounds(self) -> tuple[int, int]:
        return round(0.05 * self.scale_factor), round(0.2 * self.scale_factor)
