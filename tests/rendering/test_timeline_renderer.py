
from pathlib import Path

from PIL import Image

from backend.compositing.compositor import Compositor
from backend.rendering.timeline_renderer import TimelineRenderer
from backend.timeline.timeline_controller import TimelineController
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
    TimelineSpec,
    TimelineTrack,
    TimelineTrackType,
)


def create_timeline(tmp_path: Path):

    track = TimelineTrack(
        id="rabbit_track",
        track_type=TimelineTrackType.CHARACTER,
        target_id="rabbit",
    )

    clip = TimelineClip(
        id="rabbit_hop",
        track_id="rabbit_track",
        target_id="rabbit",
        clip_type=TimelineClipType.ACTION,
        start=1,
        duration=2,
        asset_path=tmp_path / "rabbit.png",
        params={
            "position": {
                "x": 100,
                "y": 100,
            },
            "z_index": 1,
        },
    )

    timeline = TimelineSpec(
        scene_id="test_scene",
        duration=4,
        fps=24,
        width=1280,
        height=720,
        tracks=[track],
        clips=[clip],
    )

    return TimelineController(timeline)


def test_render_active_character_frame(tmp_path):

    controller = create_timeline(tmp_path)

    clip_dir = tmp_path / "rabbit_hop"
    clip_dir.mkdir()

    Image.new(
        "RGBA",
        (1280, 720),
        (255, 0, 0, 255),
    ).save(
        clip_dir / "frame_000000.png"
    )

    renderer = TimelineRenderer(
        controller=controller,
        compositor=Compositor(1280, 720),
        output_dir=tmp_path,
    )

    # Timeline 1 second = clip's first frame.
    result = renderer.render_frame(24)

    assert result.mode == "RGBA"

    # The character's image is placed at (100, 100).
    assert result.getpixel((150, 150)) == (
        255, 0, 0, 255
    )

    assert result.getpixel((50, 50))[3] == 0


def test_render_before_clip_starts(tmp_path):

    controller = create_timeline(tmp_path)

    renderer = TimelineRenderer(
        controller=controller,
        compositor=Compositor(1280, 720),
        output_dir=tmp_path,
    )

    result = renderer.render_frame(0)

    assert result.getpixel((150, 150))[3] == 0
