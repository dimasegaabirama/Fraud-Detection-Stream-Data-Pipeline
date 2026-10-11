from enum import Enum

class ThresholdLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SegmentLevel(str, Enum):
    RETAIL = "retail"
    BUSINESS = "business"
    INDIVIDUAL = "individual"

class DirectionLevel(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class StatusLevel(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RESERVED = "reserved"

class FraudStatus(str, Enum):
    NORMAL = "normal"
    REVIEW = "review"
    FRAUD = "fraud"
    
class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"

class IPType(str, Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"

class JobMode(str, Enum):
    STREAMING = "streaming"
    BATCH = "batch"