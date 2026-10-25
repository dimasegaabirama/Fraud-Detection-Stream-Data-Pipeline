from src.rules.base_rules import BaseRules

class AmountRules(BaseRules):
    def __init__(self, settings, fraud_type, **key_select):
        super().__init__(settings, fraud_type, **key_select)

    def evaluate(self, value: float, **key_select: str) -> int:
        score = self.get_score(value, **key_select)
        return score