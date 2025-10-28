from enum import Enum


class ValidationRuleResult:
    def __init__(self, success: bool, error_message: str = "") -> None:
        self.success = success
        self.error_message = error_message


class ValidationRuleSeverity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3

    def get_message(self) -> str:
        match self:
            case ValidationRuleSeverity.INFO:
                return "ℹ️ Information:"
            case ValidationRuleSeverity.WARNING:
                return "⚠️  Warning:"
            case ValidationRuleSeverity.ERROR:
                return "❌ Error:"
