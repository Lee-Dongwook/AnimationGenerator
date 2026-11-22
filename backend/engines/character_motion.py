
import math
import shutil
import subprocess
import tempfile

from pathlib import Path

from PIL import Image

from backend.core.motion_presets import get_motion


class CharacterMotionEngine:

    def generate(
        self,
        character_path: Path,
        output_path: Path,
        background_path: Path | None = None,
        options: dict | None = None,
    ) -> Path:

        options = options or {}

        width = options.get("width", 1280)
        height = options.get("height", 720)
        fps = options.get("fps", 24)
        duration = options.get("duration", 5)
        preset = options.get("preset", "bounce")

        if not character_path.exists():
            raise FileNotFoundError(character_path)

        if background_path and not background_path.exists():
            raise FileNotFoundError(background_path)

        if not (1 <= duration <= 30):
            raise ValueError("Duration must be between 1 and 30 seconds.")

        if fps <= 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid video settings.")

        ffmpeg = shutil.which("ffmpeg")

        if not ffmpeg:
            raise RuntimeError("FFmpeg is not installed.")

        # Load character with transparency
        character = Image.open(character_path).convert("RGBA")

        # Resize character while preserving aspect ratio
        character.thumbnail(
            (width // 2, height * 3 // 4),
            Image.Resampling.LANCZOS,
        )

        # Load or create background
        if background_path:
            background = Image.open(background_path).convert("RGB")
            background = background.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )
        else:
            background = Image.new(
                "RGB",
                (width, height),
                (180, 220, 245),
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        total_frames = fps * duration

        with tempfile.TemporaryDirectory() as temp_dir:

            temp_path = Path(temp_dir)

            for frame_index in range(total_frames):

                progress = frame_index / max(total_frames - 1, 1)

                motion = get_motion(preset, progress)

                frame = background.copy().convert("RGBA")

                scale = motion["scale"]

                char_width = max(1, int(character.width * scale))
                char_height = max(1, int(character.height * scale))

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
                    (width - animated_character.width) / 2
                    + motion["x"]
                )

                y = int(
                    height * 0.72
                    - animated_character.height
                    + motion["y"]
                )

                frame.alpha_composite(
                    animated_character,
                    (x, y),
                )

                frame.convert("RGB").save(
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
