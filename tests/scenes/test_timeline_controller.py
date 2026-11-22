import pytest

from backend.timeline.timeline_controller import TimelineController
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
    TimelineSpec,
    TimelineTrack,
    TimelineTrackType,
)


def create_timeline():
    clip = TimelineClip(
        id="clip_01",
        track_id="character_01",
        target_id="character_01",
        clip_type=TimelineClipType.ACTION,
        start=2,
        duration=3,
        action_name="hop",
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


def test_get_active_clips():
    controller = TimelineController(create_timeline())

    assert len(controller.get_active_clips(1)) == 0
    assert len(controller.get_active_clips(2)) == 1
    assert len(controller.get_active_clips(3)) == 1
    assert len(controller.get_active_clips(5)) == 0


def test_get_clip_progress():
    controller = TimelineController(create_timeline())

    progress = controller.get_clip_progress(
        clip_id="clip_01",
        time=3.5,
    )

    assert progress == pytest.approx(0.5)


def test_get_frame_time():
    controller = TimelineController(create_timeline())

    assert controller.get_frame_time(24) == pytest.approx(1.0)


def test_reject_clip_exceeding_timeline():
    timeline = create_timeline()

    timeline.clips[0].duration = 20

    with pytest.raises(ValueError):
        TimelineController(timeline)
