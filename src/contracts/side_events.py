from pydantic import BaseModel
from src.contracts.raw_events import Transaction

class BaseSideEvent(BaseModel):
    info: str
    value: dict


class DeadLetterEvent(BaseSideEvent):
    info: str = "Error"


class DuplicateEvent(BaseSideEvent):
    info: str = "Duplicate"
    value: Transaction


class BlacklistEvent(BaseSideEvent):
    info: str = "Blacklist"
    value: Transaction
