from pydantic import BaseModel
from src.models.threshold import ThresholdLevelScore
from src.models.score import ScorePolicy


FactorMap = dict[str, dict[str, float]]


class HardBlockConfig(BaseModel):
    device_id: str
    ip_address: str
    user_id: str


class RuleConfig(BaseModel):
    timeout_ms: int | None = 30_000
    threshold: ThresholdLevelScore
    factors: FactorMap | None = None


class AmountRuleConfig(BaseModel):
    single: RuleConfig
    rolling: RuleConfig
    factors: FactorMap


class RulesSettings(BaseModel):
    score_policy: ScorePolicy
    hard_block: HardBlockConfig
    amount: RuleConfig
    device: RuleConfig
    ip_address: RuleConfig
    speed: RuleConfig
    velocity: RuleConfig