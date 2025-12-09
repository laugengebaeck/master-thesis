from abc import ABC, abstractmethod

import pandas as pd
from util.validation import ValidationRuleResult, ValidationRuleSeverity
from yaramo.signal import Signal, SignalFunction, SignalState


class TableValidationRule(ABC):
    severity: ValidationRuleSeverity

    @abstractmethod
    def check(self, signals: list[Signal], raw_table: pd.DataFrame) -> list[ValidationRuleResult]:
        pass


class MainAspectValidation(TableValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(self, signals: list[Signal], raw_table: pd.DataFrame) -> list[ValidationRuleResult]:
        results = []

        for signal in signals:
            if signal.function in [
                SignalFunction.Einfahr_Signal,
                SignalFunction.Ausfahr_Signal,
                SignalFunction.Zwischen_Signal,
                SignalFunction.Block_Signal,
            ]:
                if not SignalState.HP0 in signal.supported_states:
                    results.append(
                        ValidationRuleResult(
                            False, f"{signal.name} is a main signal, but cannot show Hp0."
                        )
                    )
                else:
                    results.append(ValidationRuleResult(True))

                if (
                    not SignalState.KS1 in signal.supported_states
                    or SignalState.KS2 in signal.supported_states
                ):
                    results.append(
                        ValidationRuleResult(
                            False,
                            f"{signal.name} is a main signal, but cannot show either of Ks1 and Ks2.",
                        )
                    )
                else:
                    results.append(ValidationRuleResult(True))

        return results


class DistantAspectValidation(TableValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(self, signals: list[Signal], raw_table: pd.DataFrame) -> list[ValidationRuleResult]:
        results = []

        for signal in signals:
            if signal.function == SignalFunction.Vorsignal_Vorsignalwiederholer:
                if not SignalState.KS2 in signal.supported_states:
                    results.append(
                        ValidationRuleResult(
                            False, f"{signal.name} is a distant signal, but cannot show Ks2."
                        )
                    )
                else:
                    results.append(ValidationRuleResult(True))

                if SignalState.HP0 in signal.supported_states:
                    results.append(
                        ValidationRuleResult(
                            False, f"{signal.name} is a distant signal, but is able to show Hp0."
                        )
                    )
                else:
                    results.append(ValidationRuleResult(True))

        return results


class Zs1Zs7Validation(TableValidationRule):
    severity = ValidationRuleSeverity.ERROR

    def check(self, signals: list[Signal], raw_table: pd.DataFrame) -> list[ValidationRuleResult]:
        results = []

        for signal in signals:
            if (
                SignalState.ZS1 in signal.supported_states
                and SignalState.ZS7 in signal.supported_states
            ):
                results.append(
                    ValidationRuleResult(
                        False,
                        f"{signal.name} is able to show both Zs1 and Zs7, which should not occur together.",
                    )
                )
            else:
                results.append(ValidationRuleResult(True))

        return results
