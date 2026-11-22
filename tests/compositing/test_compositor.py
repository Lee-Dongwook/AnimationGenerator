
from PIL import Image

from backend.compositing.compositor import Compositor


def test_create_transparent_canvas():

    compositor = Compositor(
        width=1280,
        height=720,
    )

    canvas = compositor.create_canvas()

    assert canvas.mode == "RGBA"
    assert canvas.size == (1280, 720)
    assert canvas.getpixel((0, 0))[3] == 0


def test_composite_character():

    compositor = Compositor(
        width=1280,
        height=720,
    )

    canvas = compositor.create_canvas()

    character = Image.new(
        "RGBA",
        (100, 100),
        (255, 0, 0, 255),
    )

    result = compositor.composite_character(
        canvas=canvas,
        character=character,
        x=100,
        y=100,
    )

    assert result.getpixel((150, 150)) == (
        255, 0, 0, 255
    )

    assert result.getpixel((50, 50))[3] == 0


def test_compose_multiple_characters_by_z_index():

    compositor = Compositor(
        width=1280,
        height=720,
    )

    red = Image.new(
        "RGBA",
        (100, 100),
        (255, 0, 0, 255),
    )

    blue = Image.new(
        "RGBA",
        (100, 100),
        (0, 0, 255, 255),
    )

    result = compositor.compose(
        background=None,
        characters=[
            {
                "image": blue,
                "position": {"x": 100, "y": 100},
                "z_index": 2,
            },
            {
                "image": red,
                "position": {"x": 100, "y": 100},
                "z_index": 1,
            },
        ],
    )

    assert result.getpixel((150, 150)) == (
        0, 0, 255, 255
    )


def test_composite_character_outside_canvas():

    compositor = Compositor(
        width=1280,
        height=720,
    )

    canvas = compositor.create_canvas()

    character = Image.new(
        "RGBA",
        (100, 100),
        (255, 0, 0, 255),
    )

    result = compositor.composite_character(
        canvas=canvas,
        character=character,
        x=-50,
        y=-50,
    )

    assert result.getpixel((0, 0)) == (
        255, 0, 0, 255
    )

    assert result.getpixel((100, 100))[3] == 0
