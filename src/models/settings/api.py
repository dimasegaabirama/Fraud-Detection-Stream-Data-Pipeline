from pydantic import BaseModel, Field

class ApiConfig(BaseModel):
    version: str
    refresh_ms: int
    base_currency: str = Field(min_length=3, max_length=3)
    path: str
    urls: list[str]

    @property
    def full_urls(self) -> list[str]:
        path = self.path.format(version=self.version, currency=self.base_currency)
        return [f"{url}{path}" for url in self.urls]

ApiSettings = dict[str, ApiConfig]