from pyflink.datastream.functions import MapFunction
from src.models.transaction import Transaction

class NormalizeTransaction(MapFunction):
    def map(self, value: dict) -> dict:
        transaction = Transaction(**value).model_dump()

        for key, value in transaction.items():
            if isinstance(value, str):
                transaction[key] = value.lower() if value else None
            if isinstance(value, float):
                transaction[key] = round(float(value), 2)

        return transaction