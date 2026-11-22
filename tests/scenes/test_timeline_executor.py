from pathlib import Path

from backend.engines.base import (
    AnimationEngine,
    ArtifactType,
    EngineRequest,
    EngineResult,
)
from backend.engines.registry import EngineRegistry
from backend.scenes.scene_schema import EngineType
from backend.timeline.timeline_controller import TimelineController
from backend.timeline.timeline_executor import TimelineExecutor
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
    TimelineSpec,
    TimelineTrack,
    TimelineTrackType,
)


class DummyEngine(AnimationEngine):

    def __init__(self):
        self.requests = []

    @property
    def engine_type(self):
        return EngineType.TRANSFORM

    def render(self, request: EngineRequest) -> EngineResult:
        self.requests.append(request)

        return EngineResult(
            output_path=request.output_path,
            artifact_type=ArtifactType.IMAGE_SEQUENCE,
            media_type="image/png",
            duration=request.duration,
            fps=request.fps,
            frame_count=round(request.duration * request.fps),
            has_alpha=True,
        )


def create_timeline(image_path: Path):

    clip = TimelineClip(
        id="character_hop",
        track_id="character_01",
        target_id="character_01",
        clip_type=TimelineClipType.ACTION,
        start=2,
        duration=3,
        engine=EngineType.TRANSFORM,
        action_name="hop",
        asset_path=image_path,
    )

    track = TimelineTrack(
        id="character_01",
        track_type=TimelineTrackType.CHARACTER,
        target_id="character_01",
        clips=[clip],
    )

    return TimelineSpec(
        scene_id="test_scene",
        duration=10,
        tracks=[track],
        clips=[clip],
    )


def test_execute_timeline(tmp_path: Path):
    image_path = tmp_path / "character.png"
    image_path.touch()

    engine = DummyEngine()

    registry = EngineRegistry()
    registry.register(engine)

    timeline = create_timeline(image_path)
    controller = TimelineController(timeline)

    executor = TimelineExecutor(
        controller=controller,
        registry=registry,
    )

    results = executor.execute(
        tmp_path / "output",
    )

    assert len(results) == 1
    assert len(engine.requests) == 1

    request = engine.requests[0]

    assert request.character_id == "character_01"
    assert request.action_name == "hop"
    assert request.duration == 3
    assert request.engine_type == EngineType.TRANSFORM

    assert results[0].clip_id == "character_hop"
    assert results[0].start == 2
    assert results[0].duration == 3


def test_execute_skips_non_action_clips(tmp_path: Path):
    timeline = create_timeline(tmp_path / "character.png")

    background_clip = TimelineClip(
        id="background_01",
        track_id="background",
        target_id="background",
        clip_type=TimelineClipType.BACKGROUND,
        start=0,
        duration=10,
    )

    background_track = TimelineTrack(
        id="background",
        track_type=TimelineTrackType.BACKGROUND,
        target_id="background",
        clips=[background_clip],
    )

    timeline.clips.append(background_clip)
    timeline.tracks.append(background_track)

    image_path = tmp_path / "character.png"
    image_path.touch()

    engine = DummyEngine()

    registry = EngineRegistry()
    registry.register(engine)

    controller = TimelineController(timeline)

    executor = TimelineExecutor(
        controller=controller,
        registry=registry,
    )

    results = executor.execute(
        tmp_path / "output",
    )

    assert len(results) == 1
    assert len(engine.requests) == 1
