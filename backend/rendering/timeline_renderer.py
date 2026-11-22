
from pathlib import Path

from PIL import Image

from backend.compositing.compositor import Compositor
from backend.timeline.timeline_controller import TimelineController
from backend.timeline.timeline_schema import (
    TimelineClip,
    TimelineClipType,
)


class TimelineRenderer:

    def __init__(
        self,
        controller: TimelineController,
        compositor: Compositor,
        output_dir: Path,
    ):
        self.controller = controller
        self.compositor = compositor
        self.output_dir = output_dir

    def render_frame(
        self,
        frame_index: int,
        background: Image.Image | None = None,
    ) -> Image.Image:

        timeline = self.controller.timeline

        time = self.controller.get_frame_time(
            frame_index
        )

        active_clips = self.controller.get_active_clips(
            time
        )

        characters = []

        for clip in active_clips:

            if clip.clip_type != TimelineClipType.ACTION:
                continue

            if clip.asset_path is None:
                continue

            characters.append(
                self._load_character_frame(
                    clip=clip,
                    time=time,
                )
            )

        return self.compositor.compose(
            background=background,
            characters=characters,
        )

    def _load_character_frame(
        self,
        clip: TimelineClip,
        time: float,
    ) -> dict:

        elapsed = time - clip.start

        local_frame_index = int(
            elapsed * self.controller.timeline.fps
        )

        frame_path = (
            self.output_dir
            / clip.id
            / f"frame_{local_frame_index:06d}.png"
        )

        if not frame_path.is_file():
            raise FileNotFoundError(
                f"Frame not found: {frame_path}"
            )

        with Image.open(frame_path) as image:
            character = image.convert("RGBA")

        params = clip.params

        return {
            "image": character,
            "position": params.get(
                "position",
                {"x": 0, "y": 0},
            ),
            "z_index": params.get("z_index", 0),
        }
