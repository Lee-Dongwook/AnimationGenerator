from pathlib import Path

from backend.engines.base import EngineRequest, EngineResult
from backend.engines.registry import EngineRegistry
from backend.scenes.scene_schema import SceneSpec


class SceneController:

    def __init__(self, registry: EngineRegistry):
        self.registry = registry

    def execute(
        self,
        scene: SceneSpec,
        output_dir: Path,
    ) -> list[EngineResult]:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        results = []

        for character in scene.characters:
            if not character.asset_path.exists():
                raise FileNotFoundError(
                    f"Character asset not found: "
                    f"{character.asset_path}"
                )

            for action_index, action in enumerate(
                character.actions
            ):
                engine = self.registry.get(action.engine)

                iteration_duration = (
                    action.duration / action.repeat
                )

                for repeat_index in range(action.repeat):

                    output_path = output_dir / (
                        f"{scene.scene_id}_"
                        f"{character.id}_"
                        f"{action_index}_"
                        f"{repeat_index}.mp4"
                    )

                    request = EngineRequest(
                        scene_id=scene.scene_id,
                        character_id=character.id,
                        engine_type=action.engine,
                        action_name=action.name,
                        image_path=character.asset_path,
                        output_path=output_path,
                        duration=iteration_duration,
                        fps=scene.fps,
                        width=scene.width,
                        height=scene.height,
                        params=action.params,
                    )

                    result = engine.render(request)
                    results.append(result)

        return results
