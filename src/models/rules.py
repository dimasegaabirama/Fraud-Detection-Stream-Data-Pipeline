from typing_extensions import List
from pydantic import BaseModel

from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold


# Base

class BaseRule(BaseModel):
    enabled: bool = True
    threshold: FraudThreshold


class BaseFraudRule(BaseModel):
    segment: Segment
    direction: Direction
    transaction_type: TransactionType
    rule: BaseRule


class BaseFraudRulesConfig(BaseModel):
    rules: List[BaseFraudRule]


# Amount

class AmountRule(BaseRule):
    pass


class AmountFraudRule(BaseFraudRule):
    rule: AmountRule


class AmountFraudRulesConfig(BaseFraudRulesConfig):
    rules: List[AmountFraudRule]


# Velocity

class VelocityRule(BaseRule):
    pass


class VelocityFraudRule(BaseFraudRule):
    rule: VelocityRule


class VelocityFraudRulesConfig(BaseFraudRulesConfig):
    rules: List[VelocityFraudRule]


# Device

class DeviceRule(BaseRule):
    pass


class DeviceFraudRule(BaseFraudRule):
    rule: DeviceRule


class DeviceFraudRulesConfig(BaseFraudRulesConfig):
    rules: List[DeviceFraudRule]


# IP Address

class IPAddressRule(BaseRule):
    pass


class IPAddressFraudRule(BaseFraudRule):
    rule: IPAddressRule


class IPAddressFraudRulesConfig(BaseFraudRulesConfig):
    rules: List[IPAddressFraudRule]


# Speed

class SpeedRule(BaseRule):
    pass


class SpeedFraudRule(BaseFraudRule):
    rule: SpeedRule


class SpeedFraudRulesConfig(BaseFraudRulesConfig):
    rules: List[SpeedFraudRule]