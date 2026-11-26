from pydantic import BaseModel, model_validator
from src.models.threshold import ThresholdLevelScore
from src.models.enums import Aggregation


FactorMap = dict[str, dict[str, float]]


class RulePolicy(BaseModel):
    otp: int
    review: int
    block: int

    @model_validator(mode="after")
    def _validate_order(self):
        if not (self.otp < self.review < self.block):
            raise ValueError("Threshold values must be ascending: allow < otp < review < block.")
        return self


class RuleConfig(BaseModel):
    window_ms: int | None = None
    threshold: ThresholdLevelScore
    factors: FactorMap | None = None


class AmountRuleConfig(BaseModel):
    single: RuleConfig
    rolling: RuleConfig
    factors: FactorMap


class RulesSettings(BaseModel):
    global_window_size_ms: int
    global_window_slide_ms: int
    rule_policy: RulePolicy
    amount: AmountRuleConfig
    device: RuleConfig
    ip_address: RuleConfig
    speed: RuleConfig
    velocity: RuleConfig