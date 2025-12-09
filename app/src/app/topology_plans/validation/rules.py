import math
from abc import ABC, abstractmethod

import networkx as nx
from topology_plans.thresholds import TopologyThresholds
from util.validation import ValidationRuleResult, ValidationRuleSeverity
from util.vector import Vector2D


class TopologyValidationRule(ABC):
    severity: ValidationRuleSeverity

    def __init__(self, thresholds: TopologyThresholds) -> None:
        self.thresholds = thresholds

    @abstractmethod
    def check(
        self, topology: nx.Graph, switch_positions: list[Vector2D]
    ) -> list[ValidationRuleResult]:
        pass


class NeighborCountValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(
        self, topology: nx.Graph, switch_positions: list[Vector2D]
    ) -> list[ValidationRuleResult]:
        results = []

        for node in topology.nodes:
            if topology.degree[node] >= 4:  # type: ignore
                results.append(
                    ValidationRuleResult(
                        False,
                        f"In the created topology, node {node} has more than 3 neighbors.",
                    )
                )
            else:
                results.append(ValidationRuleResult(True))
        return results


class NoSwitchSymbolValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.WARNING

    def check(
        self, topology: nx.Graph, switch_positions: list[Vector2D]
    ) -> list[ValidationRuleResult]:
        results = []

        for node in topology.nodes:
            if topology.degree[node] == 3 and not any(math.dist(node, switch.to_tuple()) <= self.thresholds.same_node_distance() for switch in switch_positions):  # type: ignore
                results.append(
                    ValidationRuleResult(
                        False,
                        f"In the created topology, node {node} functions as a switch, but no switch symbol was found there.",
                    )
                )
            else:
                results.append(ValidationRuleResult(True))

        return results


class SwitchSymbolWithoutFunctionValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.WARNING

    def check(
        self, topology: nx.Graph, switch_positions: list[Vector2D]
    ) -> list[ValidationRuleResult]:
        results = []

        for switch in switch_positions:
            if not any(topology.degree[node] == 3 and math.dist(node, switch.to_tuple()) <= self.thresholds.same_node_distance() for node in topology.nodes):  # type: ignore
                results.append(
                    ValidationRuleResult(
                        False,
                        f"In the created topology, a switch symbol was found at position {switch.to_tuple()}, but there is no node that functions as a switch there.",
                    )
                )
            else:
                results.append(ValidationRuleResult(True))

        return results
