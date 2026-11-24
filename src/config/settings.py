from pathlib import Path

from pydantic import model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from src.models.settings import *
from src.models.endpoint import KafkaEndpoint, HiveEndpoint

class AppSettings(BaseSettings):
    kafka: KafkaSettings
    hadoop: HadoopSettings
    hive: HiveSettings
    redis: RedisSettings
    pipeline: PipelineSettings
    sources: SourceSettings
    sinks: SinkSettings
    api: ApiSettings
    rules: RulesSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        env_nested_delimiter="__",
        extra="ignore",
        yaml_file=Path(__file__).parent / "config.yaml",
        yaml_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


    @model_validator(mode="after")
    def set_default_sources_and_sinks(self):

        pipeline = self.pipeline
        sources = list(self.sources.items())
        sinks = list(self.sinks.items())

        merged_endpoints = sources + sinks

        for _, endpoint in merged_endpoints:
            if isinstance(endpoint, HiveEndpoint):
                if endpoint.catalog is None:
                    endpoint.catalog = pipeline.catalog
                if endpoint.database is None:
                    endpoint.database = pipeline.database
            elif isinstance(endpoint, KafkaEndpoint):
                if endpoint.bootstrap_servers is None:
                    endpoint.bootstrap_servers = self.kafka.bootstrap_servers
                if endpoint.username is None:
                    endpoint.username = self.kafka.username
                if endpoint.password is None:
                    endpoint.password = self.kafka.password

        return self


if __name__ == "__main__":
    settings = AppSettings()
    print(settings.rules.speed)

