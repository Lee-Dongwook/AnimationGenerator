from dataclasses import dataclass
from pathlib import Path

from backend.engines.base import (
    EngineRequest,
    EngineResult,
)
from backend.engines.registry import EngineRegistry
from backend.scenes.scene_schema import EngineType
from backend.timeline.timeline_controller import TimelineController
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
)


@dataclass
class ExecutedClip:
    clip_id: str
    start: float
    duration: float
    result: EngineResult


class TimelineExecutor:

    def __init__(
        self,
        controller: TimelineController,
        registry: EngineRegistry,
    ):
        self.controller = controller
        self.registry = registry

    def execute(
        self,
        output_dir: Path,
    ) -> list[ExecutedClip]:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timeline = self.controller.timeline

        results = []

        # Timeline 순서에 따라 Clip 실행
        ordered_clips = sorted(
            timeline.clips,
            key=lambda clip: (
                clip.start,
                clip.track_id,
                clip.id,
            ),
        )

        for index, clip in enumerate(ordered_clips):

            if clip.clip_type != TimelineClipType.ACTION:
                continue

            result = self._execute_clip(
                clip=clip,
                output_path=output_dir / f"clip_{index:04d}",
            )

            results.append(
                ExecutedClip(
                    clip_id=clip.id,
                    start=clip.start,
                    duration=clip.duration,
                    result=result,
                )
            )

        return results

    def _execute_clip(
        self,
        clip: TimelineClip,
        output_path: Path,
    ) -> EngineResult:

        if clip.engine is None:
            raise ValueError(
                f"Engine is required for action clip: {clip.id}"
            )

        if clip.asset_path is None:
            raise ValueError(
                f"Asset path is required for clip: {clip.id}"
            )

        if not clip.action_name:
            raise ValueError(
                f"Action name is required for clip: {clip.id}"
            )

        if not clip.asset_path.is_file():
            raise FileNotFoundError(
                f"Character asset not found: {clip.asset_path}"
            )

        engine = self.registry.get(clip.engine)

        request = EngineRequest(
            scene_id=self.controller.timeline.scene_id,
            character_id=clip.target_id,
            engine_type=clip.engine,
            action_name=clip.action_name,
            image_path=clip.asset_path,
            output_path=output_path,
            duration=clip.duration,
            fps=self.controller.timeline.fps,
            width=self.controller.timeline.width,
            height=self.controller.timeline.height,
            params=clip.params,
        )

        return engine.render(request)
