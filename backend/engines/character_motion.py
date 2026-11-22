
import math
import shutil
import subprocess
import tempfile

from pathlib import Path

from PIL import Image

from backend.core.motion_presets import get_motion
from backend.engines.base import (
    AnimationEngine,
    ArtifactType,
    EngineRequest,
    EngineResult,
)

from backend.rendering.frame_renderer import FrameRenderer
from backend.scenes.scene_schema import EngineType

class CharacterMotionEngine(AnimationEngine):

    @property
    def engine_type(self) -> EngineType:
        return EngineType.TRANSFORM

    def render(
        self,
        request: EngineRequest,
    ) -> EngineResult:

        if not request.image_path.is_file():
            raise FileNotFoundError(request.image_path)

        if request.duration <= 0:
            raise ValueError("Duration must be positive.")

        if request.fps <= 0:
            raise ValueError("FPS must be positive.")

        if request.width <= 0 or request.height <= 0:
            raise ValueError("Invalid frame dimensions.")

        preset = request.params.get("preset", "bounce")

        character = Image.open(
            request.image_path
        ).convert("RGBA")

        character.thumbnail(
            (
                request.width // 2,
                request.height * 3 // 4,
            ),
            Image.Resampling.LANCZOS,
        )

        renderer = FrameRenderer(
            width=request.width,
            height=request.height,
        )

        total_frames = round(
            request.fps * request.duration
        )

        request.output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        for frame_index in range(total_frames):

            progress = frame_index / max(
                total_frames - 1,
                1,
            )

            motion = get_motion(
                preset,
                progress,
            )

            frame = renderer.create_canvas()

            scale = motion["scale"]

            char_width = max(
                1,
                int(character.width * scale),
            )

            char_height = max(
                1,
                int(character.height * scale),
            )

            animated_character = character.resize(
                (char_width, char_height),
                Image.Resampling.LANCZOS,
            )

            animated_character = animated_character.rotate(
                motion["rotation"],
                resample=Image.Resampling.BICUBIC,
                expand=True,
            )

            x = int(
                (request.width - animated_character.width) / 2
                + motion["x"]
            )

            y = int(
                request.height * 0.72
                - animated_character.height
                + motion["y"]
            )

            # Clip the character image to the canvas.
            left = max(0, x)
            top = max(0, y)

            right = min(
                request.width,
                x + animated_character.width,
            )

            bottom = min(
                request.height,
                y + animated_character.height,
            )

            if left < right and top < bottom:

                character_crop = animated_character.crop(
                    (
                        left - x,
                        top - y,
                        right - x,
                        bottom - y,
                    )
                )

                frame.alpha_composite(
                    character_crop,
                    (left, top),
                )

            renderer.save_frame(
                image=frame,
                output_path=(
                    request.output_path
                    / f"frame_{frame_index:06d}.png"
                ),
            )

        return EngineResult(
            output_path=request.output_path,
            artifact_type=ArtifactType.IMAGE_SEQUENCE,
            media_type="image/png",
            duration=request.duration,
            fps=request.fps,
            frame_count=total_frames,
            has_alpha=True,
            metadata={
                "preset": preset,
                "character_id": request.character_id,
                "width": request.width,
                "height": request.height,
            },
        )
