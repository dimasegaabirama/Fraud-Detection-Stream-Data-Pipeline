from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


from src.models.rules import RulesSettings


# class AppSettings(BaseSettings):
#     kafka: KafkaSettings
#     hadoop: HadoopSettings
#     hive: HiveSettings
#     pipeline: PipelineSettings
#     rules: RulesSettings

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         env_ignore_empty=True,
#         env_nested_delimiter="__",
#         extra="ignore",
#         yaml_file=Path(__file__).parent / "config.yaml",
#         yaml_file_encoding="utf-8",
#     )

#     @classmethod
#     def settings_customise_sources(
#         cls,
#         settings_cls: type[BaseSettings],
#         init_settings: PydanticBaseSettingsSource,
#         env_settings: PydanticBaseSettingsSource,
#         dotenv_settings: PydanticBaseSettingsSource,
#         file_secret_settings: PydanticBaseSettingsSource,
#     ) -> tuple[PydanticBaseSettingsSource, ...]:
#         return (
#             init_settings,
#             env_settings,
#             dotenv_settings,
#             YamlConfigSettingsSource(settings_cls),
#             file_secret_settings,
#         )


# if __name__ == "__main__":
#     settings = AppSettings()
#     print(settings.rules)
