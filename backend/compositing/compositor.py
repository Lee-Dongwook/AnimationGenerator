
from pathlib import Path

from PIL import Image


class Compositor:

    def __init__(
        self,
        width: int,
        height: int,
    ):
        if width <= 0 or height <= 0:
            raise ValueError("Invalid canvas dimensions.")

        self.width = width
        self.height = height

    def create_canvas(
        self,
        background: Image.Image | None = None,
    ) -> Image.Image:

        if background is None:
            return Image.new(
                "RGBA",
                (self.width, self.height),
                (0, 0, 0, 0),
            )

        background = background.convert("RGBA")

        return background.resize(
            (self.width, self.height),
            Image.Resampling.LANCZOS,
        )

    def composite_character(
        self,
        canvas: Image.Image,
        character: Image.Image,
        x: int,
        y: int,
    ) -> Image.Image:

        character = character.convert("RGBA")

        left = max(0, x)
        top = max(0, y)

        right = min(
            self.width,
            x + character.width,
        )

        bottom = min(
            self.height,
            y + character.height,
        )

        if left >= right or top >= bottom:
            return canvas

        cropped_character = character.crop(
            (
                left - x,
                top - y,
                right - x,
                bottom - y,
            )
        )

        canvas.alpha_composite(
            cropped_character,
            (left, top),
        )

        return canvas

    def compose(
        self,
        background: Image.Image | None,
        characters: list[dict],
    ) -> Image.Image:

        canvas = self.create_canvas(background)

        ordered_characters = sorted(
            characters,
            key=lambda item: item.get("z_index", 0),
        )

        for item in ordered_characters:

            image = item["image"]

            position = item.get(
                "position",
                {},
            )

            x = int(position.get("x", 0))
            y = int(position.get("y", 0))

            self.composite_character(
                canvas=canvas,
                character=image,
                x=x,
                y=y,
            )

        return canvas
