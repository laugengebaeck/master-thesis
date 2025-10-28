from abc import ABC, abstractmethod

import networkx as nx
from topology_plans.thresholds import TopologyThresholds
from topology_plans.vector import Vector2D
from util import ValidationRuleResult, ValidationRuleSeverity


class TopologyValidationRule(ABC):
    severity: ValidationRuleSeverity

    def __init__(self, thresholds: TopologyThresholds) -> None:
        self.thresholds = thresholds

    @abstractmethod
    def check(self, topology: nx.Graph, switch_positions: list[Vector2D]) -> ValidationRuleResult:
        pass


class NeighborCountValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.WARNING

    def check(self, topology: nx.Graph, switch_positions: list[Vector2D]) -> ValidationRuleResult:
        for node in topology.nodes:
            if topology.degree[node] >= 4:  # type: ignore
                return ValidationRuleResult(
                    False,
                    f"In the created topology, node {node} has more than 3 neighbors.",
                )
        return ValidationRuleResult(True)


class SwitchSymbolValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(self, topology: nx.Graph, switch_positions: list[Vector2D]) -> ValidationRuleResult:
        for node in topology.nodes:
            if G.degree[node] == 3 and all(math.dist(node, switch.to_tuple()) > self.thresholds.same_node_distance() for switch in switch_positions):  # type: ignore
                # TODO umgekehrt auch Dreieck, aber keine Weiche
                return ValidationRuleResult(
                    False,
                    f"In the created topology, node {node} functions as a switch, but no switch symbol was found there.",
                )
        return ValidationRuleResult(True)


class NoCyclesValidation(TopologyValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(self, topology: nx.Graph, switch_positions: list[Vector2D]) -> ValidationRuleResult:
        cycles = sorted(nx.simple_cycles(topology))
        if len(cycles) > 0:
            return ValidationRuleResult(False, f"The created topology contains cycles: {cycles}")
        return ValidationRuleResult(True)
