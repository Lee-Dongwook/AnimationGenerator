from pathlib import Path

from PIL import Image


class FrameRenderer:

    def __init__(
        self,
        width: int,
        height: int,
    ):
        self.width = width
        self.height = height

    def create_canvas(self) -> Image.Image:
        return Image.new(
            "RGBA",
            (self.width, self.height),
            (0, 0, 0, 0),
        )

    def save_frame(
        self,
        image: Image.Image,
        output_path: Path,
    ) -> None:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        if image.size != (self.width, self.height):
            raise ValueError(
                "Frame dimensions do not match renderer dimensions"
            )

        image.save(
            output_path,
            format="PNG",
        )

    def render_sequence(
        self,
        frames: list[Image.Image],
        output_dir: Path,
    ) -> int:

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for index, frame in enumerate(frames):
            self.save_frame(
                image=frame,
                output_path=output_dir / f"frame_{index:06d}.png",
            )

        return len(frames)
