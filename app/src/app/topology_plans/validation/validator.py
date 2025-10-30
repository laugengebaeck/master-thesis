import networkx as nx
from topology_plans.thresholds import TopologyThresholds
from topology_plans.validation.rules import (
    NeighborCountValidation,
    NoCyclesValidation,
    SwitchSymbolValidation,
    TopologyValidationRule,
)
from util.validation import ValidationRuleSeverity
from util.vector import Vector2D


class TopologyValidator:
    def __init__(self, thresholds: TopologyThresholds) -> None:
        self.rules: list[TopologyValidationRule] = [
            NeighborCountValidation(thresholds),
            SwitchSymbolValidation(thresholds),
            NoCyclesValidation(thresholds),
        ]

    def check(self, topology: nx.Graph, switch_positions: list[Vector2D]) -> bool:
        validation_failed = False
        print()
        print("[Validation Results]")
        for rule in self.rules:
            result = rule.check(topology, switch_positions)
            if not result.success:
                print(f"{rule.severity.get_message()} {result.error_message}")
                if rule.severity == ValidationRuleSeverity.ERROR:
                    validation_failed = True
        print()
        return validation_failed
