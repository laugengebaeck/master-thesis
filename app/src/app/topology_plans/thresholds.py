from typing import Any


class TopologyThresholds:
    def __init__(self, config: dict[str, Any], width: int, height: int) -> None:
        self.config = config
        self.scale = min(width, height)

    def similar_line_distance(self) -> int:
        return round(self.config["similar_line_distance"] * self.scale)

    def min_line_length(self) -> int:
        return round(self.config["min_line_length"] * self.scale)

    def max_line_gap(self) -> int:
        return round(self.config["max_line_gap"] * self.scale)

    def same_node_distance(self) -> int:
        return round(self.config["same_node_distance"] * self.scale)

    def max_spur_length(self) -> int:
        return round(self.config["max_spur_length"] * self.scale)

    def on_edge_dist(self) -> int:
        return round(self.config["on_edge_dist"] * self.scale)

    def switch_area_bounds(self) -> tuple[int, int]:
        return round(self.config["switch_area_bounds"]["min"] * self.scale), round(
            self.config["switch_area_bounds"]["max"] * self.scale
        )
