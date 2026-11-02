from src.application.bootstrap.registry import SINK_REGISTRY, SOURCE_REGISTRY
from src.config.settings import AppSettings


def test_configured_endpoints_have_registered_models() -> None:
    settings = AppSettings()

    assert all(
        source.name in SOURCE_REGISTRY for source in settings.pipeline.sources
    )
    assert all(sink.name in SINK_REGISTRY for sink in settings.pipeline.sinks)