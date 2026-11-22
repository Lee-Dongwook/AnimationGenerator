from backend.engines.base import AnimationEngine
from backend.scenes.scene_schema import EngineType


class EngineRegistry:

    def __init__(self):
        self._engines: dict[EngineType, AnimationEngine] = {}

    def register(self, engine: AnimationEngine) -> None:
        engine_type = engine.engine_type

        if engine_type in self._engines:
            raise ValueError(
                f"Engine already registered: {engine_type}"
            )

        self._engines[engine_type] = engine

    def get(self, engine_type: EngineType) -> AnimationEngine:
        engine = self._engines.get(engine_type)

        if engine is None:
            raise ValueError(
                f"Engine not registered: {engine_type}"
            )

        return engine

    def has(self, engine_type: EngineType) -> bool:
        return engine_type in self._engines
