from pydantic import BaseModel
from src.contracts.cleaned_events import CleanedTransaction

class BaseSideEvents(BaseModel):
    info: str
    value: dict


class DeadLetterEvents(BaseSideEvents):
    info: str = "Error"


class DuplicateEvents(BaseSideEvents):
    info: str = "Duplicate"
    value: CleanedTransaction
