
import shutil
import subprocess
import tempfile

from pathlib import Path

from PIL import Image, ImageOps

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

    def generate(
        self,
        character_path: Path,
        background_path: Path | None,
        output_path: Path,
        options: dict,
    ) -> Path:
        """Render a transparent character sequence and encode it as an MP4."""
        ffmpeg = shutil.which("ffmpeg")

        if not ffmpeg:
            raise RuntimeError("FFmpeg is not installed.")

        width = options.get("width", 1280)
        height = options.get("height", 720)
        fps = options.get("fps", 24)
        duration = options.get("duration", 5)
        preset = options.get("preset", "bounce")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            frame_dir = Path(temp_dir) / "frames"
            result = self.render(
                EngineRequest(
                    scene_id="character_video",
                    character_id="character",
                    engine_type=self.engine_type,
                    action_name=preset,
                    image_path=character_path,
                    output_path=frame_dir,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    params={"preset": preset},
                )
            )

            self._apply_background(
                frame_dir=frame_dir,
                background_path=background_path,
                width=width,
                height=height,
            )

            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-framerate", str(fps),
                    "-i", str(frame_dir / "frame_%06d.png"),
                    "-frames:v", str(result.frame_count),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        return output_path

    @staticmethod
    def _apply_background(
        frame_dir: Path,
        background_path: Path | None,
        width: int,
        height: int,
    ) -> None:
        if background_path:
            with Image.open(background_path) as image:
                background = ImageOps.fit(
                    image.convert("RGB"),
                    (width, height),
                    method=Image.Resampling.LANCZOS,
                )
        else:
            background = Image.new("RGB", (width, height), "#f7f4fc")

        for frame_path in sorted(frame_dir.glob("frame_*.png")):
            with Image.open(frame_path) as frame:
                composited = background.copy()
                composited.paste(frame, mask=frame.getchannel("A"))
                composited.save(frame_path, format="PNG")
