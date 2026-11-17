from pydantic import BaseModel
from src.contracts.raw_events import Transaction

class BaseSideEvents(BaseModel):
    info: str
    value: dict


class DeadLetterEvents(BaseSideEvents):
    info: str = "Error"


class DuplicateEvents(BaseSideEvents):
    info: str = "Duplicate"
    value: Transaction
