from pydantic import BaseModel, model_validator, Field

from src.models.enums import FraudStatus


class ScorePolicy(BaseModel):
    allow_below: int = Field(gt=0)
    otp_below: int = Field(gt=0)
    review_below: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_order(self):
        if not (
            0 <= self.allow_below < self.otp_below < self.review_below
        ):
            raise ValueError(
                "Score policy thresholds must be ordered: "
                "0 <= allow_below < otp_below < review_below."
            )
        return self

    def classify(self, score: int) -> FraudStatus:
        fraud_status = FraudStatus.__members__.values()

        for status in fraud_status:
            if status != FraudStatus.BLOCK and score < getattr(self, f"{status}_below"):
                return status
        return FraudStatus.BLOCK

if __name__ == "__main__":
    policy = ScorePolicy(allow_below=10, otp_below=20, review_below=30)
    print(policy.classify(5))   # Output: FraudStatus.ALLOW
    print(policy.classify(15))  # Output: FraudStatus.OTP
    print(policy.classify(25))  # Output: FraudStatus.REVIEW
    print(policy.classify(35))  # Output: FraudStatus.BLOCK