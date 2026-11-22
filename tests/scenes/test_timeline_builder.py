from pathlib import Path

from backend.scenes.scene_schema import (
    ActionSpec,
    CharacterSpec,
    EngineType,
    SceneSpec,
)
from backend.timeline.timeline_builder import TimelineBuilder
from backend.timeline.timeline_schema import (
    TimelineClipType,
    TimelineTrackType,
)


def test_build_character_timeline(tmp_path: Path):
    image_path = tmp_path / "character.png"
    image_path.touch()

    scene = SceneSpec(
        scene_id="test_scene",
        duration=7,
        characters=[
            CharacterSpec(
                id="character_01",
                asset_path=image_path,
                actions=[
                    ActionSpec(
                        engine=EngineType.TRANSFORM,
                        name="idle",
                        duration=2,
                    ),
                    ActionSpec(
                        engine=EngineType.TRANSFORM,
                        name="hop",
                        duration=3,
                        repeat=3,
                    ),
                ],
            )
        ],
    )

    timeline = TimelineBuilder().build(scene)

    assert len(timeline.tracks) == 1
    assert len(timeline.clips) == 4

    clips = timeline.clips

    assert clips[0].start == 0
    assert clips[0].duration == 2

    assert clips[1].start == 2
    assert clips[1].duration == 1

    assert clips[2].start == 3
    assert clips[3].start == 4


def test_build_background_timeline(tmp_path: Path):
    image_path = tmp_path / "character.png"
    image_path.touch()

    scene = SceneSpec(
        scene_id="background_scene",
        duration=5,
        background="forest",
        characters=[
            CharacterSpec(
                id="character_01",
                asset_path=image_path,
                actions=[],
            )
        ],
    )

    timeline = TimelineBuilder().build(scene)

    background_track = next(
        track
        for track in timeline.tracks
        if track.track_type == TimelineTrackType.BACKGROUND
    )

    assert len(background_track.clips) == 1

    assert (
        background_track.clips[0].clip_type
        == TimelineClipType.BACKGROUND
    )
