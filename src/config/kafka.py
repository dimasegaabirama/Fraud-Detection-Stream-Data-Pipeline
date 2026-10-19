from pydantic import BaseModel, SecretStr

class KafkaSettings(BaseModel):
    version: str
    bootstrap_servers: str
    username: str
    password: SecretStr