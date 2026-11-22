import math
import shutil
import subprocess
import tempfile

from pathlib import Path
from PIL import Image, ImageOps

from backend.engines.base import VideoGenerationEngine


class MotionEngine(VideoGenerationEngine):

    def generate(
        self,
        image_path: Path,
        output_path: Path,
        options: dict,
    ) -> Path:
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        ffmpeg = shutil.which("ffmpeg")

        if not ffmpeg:
            raise RuntimeError("FFmpeg is not installed.")
        
        width = options.get("width", 1280)
        height = options.get("height", 720)
        fps = options.get("fps", 24)
        duration = options.get("duration", 5)
        zoom_strength = options.get("zoom_strength", 0.15)

        if not (1 <= duration <= 30):
            raise ValueError("Duration must be between 1 and 30 seconds.")

        if not (0 <= zoom_strength <= 0.5):
            raise ValueError("Zoom strength must be between 0 and 0.5.")

        if width <= 0 or height <= 0 or fps <= 0:
            raise ValueError("Invalid video dimensions or FPS.")
        
        total_frames = fps * duration

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with Image.open(image_path) as source:
            base_image = ImageOps.fit(
                source.convert("RGB"),
                (width, height),
                method=Image.Resampling.LANCZOS,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for frame_index in range(total_frames):

                progress = frame_index / max(total_frames - 1, 1)

                eased = 0.5 - 0.5 * math.cos(
                    math.pi * progress
                )

                scale = 1.0 + zoom_strength * eased

                scaled_width = round(width * scale)
                scaled_height = round(height * scale)

                frame = base_image.resize(
                    (scaled_width, scaled_height),
                    Image.Resampling.LANCZOS,
                )

                left = (scaled_width - width) // 2
                top = (scaled_height - height) // 2

                frame = frame.crop(
                    (left, top, left + width, top + height)
                )

                frame.save(
                    temp_path / f"frame_{frame_index:05d}.jpg",
                    quality=95,
                )

            command = [
                ffmpeg,
                "-y",
                "-framerate", str(fps),
                "-i", str(temp_path / "frame_%05d.jpg"),
                "-frames:v", str(total_frames),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                str(output_path),
            ]

            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        
        return output_path

