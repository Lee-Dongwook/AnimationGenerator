import pytest

from backend.engines.base import (
    AnimationEngine,
    EngineRequest,
    EngineResult,
)
from backend.engines.registry import EngineRegistry
from backend.scenes.scene_schema import EngineType


class DummyEngine(AnimationEngine):

    @property
    def engine_type(self):
        return EngineType.TRANSFORM

    def render(self, request: EngineRequest) -> EngineResult:
        return EngineResult(
            output_path=request.output_path,
            media_type="video",
            duration=request.duration,
            fps=request.fps,
        )


def test_register_engine():
    registry = EngineRegistry()
    engine = DummyEngine()

    registry.register(engine)

    assert registry.has(EngineType.TRANSFORM)


def test_get_engine():
    registry = EngineRegistry()
    engine = DummyEngine()

    registry.register(engine)

    assert registry.get(EngineType.TRANSFORM) is engine


def test_duplicate_registration():
    registry = EngineRegistry()

    registry.register(DummyEngine())

    with pytest.raises(ValueError):
        registry.register(DummyEngine())


def test_missing_engine():
    registry = EngineRegistry()

    with pytest.raises(ValueError):
        registry.get(EngineType.AI_VIDEO)
