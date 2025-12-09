import pandas as pd
from table_plans.validation.rules import (
    DistantAspectValidation,
    MainAspectValidation,
    TableValidationRule,
    Zs1Zs7Validation,
)
from util.validation import ValidationRuleSeverity
from yaramo.signal import Signal


class TopologyValidator:
    def __init__(self) -> None:
        self.rules: list[TableValidationRule] = [
            MainAspectValidation(),
            DistantAspectValidation(),
            Zs1Zs7Validation(),
        ]

    def check(self, signals: list[Signal], raw_table: pd.DataFrame) -> bool:
        validation_failed = False
        print()
        print("[Table Validation Results]")
        for rule in self.rules:
            results = rule.check(signals, raw_table)
            for result in results:
                if not result.success:
                    print(f"{rule.severity.get_message()} {result.error_message}")
                    if rule.severity == ValidationRuleSeverity.ERROR:
                        validation_failed = True
        print()
        return validation_failed
