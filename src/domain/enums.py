from enum import Enum


class ThresholdLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Segment(str, Enum):
    RETAIL = "RETAIL"
    BUSINESS = "BUSINESS"
    INDIVIDUAL = "INDIVIDUAL"


class Direction(str, Enum):
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


class JobMode(str, Enum):
    STREAMING = "STREAMING"
    BATCH = "BATCH"