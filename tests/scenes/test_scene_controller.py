from pathlib import Path

from backend.engines.base import (
    AnimationEngine,
    EngineRequest,
    EngineResult,
)
from backend.engines.registry import EngineRegistry
from backend.scenes.scene_controller import SceneController
from backend.scenes.scene_schema import (
    ActionSpec,
    CharacterSpec,
    EngineType,
    SceneSpec,
)


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


def test_scene_execution(tmp_path: Path):
    image_path = tmp_path / "character.png"
    image_path.touch()

    registry = EngineRegistry()
    registry.register(DummyEngine())

    scene = SceneSpec(
        scene_id="test_scene",
        duration=4,
        characters=[
            CharacterSpec(
                id="character_01",
                asset_path=image_path,
                actions=[
                    ActionSpec(
                        engine=EngineType.TRANSFORM,
                        name="bounce",
                        duration=4,
                        repeat=2,
                    )
                ],
            )
        ],
    )

    controller = SceneController(registry)

    results = controller.execute(
        scene,
        tmp_path / "output",
    )

    assert len(results) == 2
    assert results[0].duration == 2
    assert results[1].duration == 2
