from typing_extensions import List
from pydantic import BaseModel, Field

from src.models.threshold import FraudThreshold, Threshold
from src.domain.enums import DirectionLevel, SegmentLevel


# Base classes for rules

class BaseRule(BaseModel):
    enabled: bool = True
    threshold: FraudThreshold

class BaseSegmentDirectionRule(BaseModel):
    segment: SegmentLevel
    direction: DirectionLevel
    rule: BaseRule

class BaseRulesConfig(BaseModel):
    rules: List[BaseSegmentDirectionRule]


# Amount rules

class AmountRule(BaseRule):
    pass

class AmountSegmentDirectionRule(BaseSegmentDirectionRule):
    rule: AmountRule

class AmountRulesConfig(BaseRulesConfig):
    rules: List[AmountSegmentDirectionRule]


# Velocity rules

class VelocityRule(BaseRule):
    pass

class VelocitySegmentDirectionRule(BaseSegmentDirectionRule):
    rule: VelocityRule

class VelocityRulesConfig(BaseRulesConfig):
    rules: List[VelocitySegmentDirectionRule]


# Device rules

class DeviceRule(BaseRule):
    pass

class DeviceSegmentDirectionRule(BaseSegmentDirectionRule):
    rule: DeviceRule

class DeviceRulesConfig(BaseRulesConfig):
    rules: List[DeviceSegmentDirectionRule]


# IP Address rules

class IPAddressRule(BaseRule):
    pass

class IPAddressSegmentDirectionRule(BaseSegmentDirectionRule):
    rule: IPAddressRule

class IPAddressRulesConfig(BaseRulesConfig):
    rules: List[IPAddressSegmentDirectionRule]


# Speed rules

class SpeedRule(BaseRule):
    pass

class SpeedSegmentDirectionRule(BaseSegmentDirectionRule):
    rule: SpeedRule

class SpeedRulesConfig(BaseRulesConfig):
    rules: List[SpeedSegmentDirectionRule]