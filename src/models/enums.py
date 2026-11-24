from enum import Enum


class FlowDirection(str, Enum):
    SINK = "sink"
    SOURCE = "source"


class Aggregation(str, Enum):
    AVG = "avg"
    SUM = "sum"
    MAX = "max"
    MIN = "min"
    COUNT = "count"
    CUSTOM = "custom"


class SegmentType(str, Enum):
    RETAIL = "retail"
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class TransactionDirection(str, Enum):
    IN = "in"
    OUT = "out"


class TransactionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RESERVED = "reserved"


class TransactionType(str, Enum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    CASHOUT = "cashout"
    TOP_UP = "top_up"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"


class FraudAction(str, Enum):
    ALLOW = "allow"
    OTP = "otp"
    BLOCK = "block"
    REVIEW = "review"


class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class IPType(str, Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"


class FraudType(str, Enum):
    AMOUNT = "amount"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"
    SPEED = "speed"
    VELOCITY = "velocity"


class ThresholdLevelType(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    NONE = "none"


class SchemaLevel(str, Enum):
    CATALOG = "catalog"
    DATABASE = "database"
    TABLE = "table"


class BlacklistType(str, Enum):
    USER_ID = "user_id"
    IP_ADDRESS = "ip_address"