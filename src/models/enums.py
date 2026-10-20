from enum import Enum


class FlowDirection(str, Enum):
    SINK = "SINK"
    SOURCE = "SOURCE"


class ThresholdLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Aggregation(str, Enum):
    AVG = "AVG"
    SUM = "SUM"
    MAX = "MAX"
    MIN = "MIN"
    COUNT = "COUNT"
    CUSTOM = "CUSTOM"


class SegmentType(str, Enum):
    RETAIL = "RETAIL"
    BUSINESS = "BUSINESS"
    INDIVIDUAL = "INDIVIDUAL"


class TransactionDirection(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class TransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RESERVED = "RESERVED"


class TransactionType(str, Enum):
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    CASHOUT = "CASHOUT"
    TOP_UP = "TOP_UP"
    WITHDRAWAL = "WITHDRAWAL"
    REFUND = "REFUND"


class FraudStatus(str, Enum):
    NORMAL = "NORMAL"
    REVIEW = "REVIEW"
    FRAUD = "FRAUD"


class DeviceType(str, Enum):
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"


class IPType(str, Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"


class EnvType(str, Enum):
    STREAMING = "STREAMING"
    TABLE = "TABLE"
