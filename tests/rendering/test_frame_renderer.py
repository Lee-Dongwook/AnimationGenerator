from PIL import Image

from backend.rendering.frame_renderer import FrameRenderer


def test_create_transparent_canvas():
    renderer = FrameRenderer(
        width=1280,
        height=720,
    )

    canvas = renderer.create_canvas()

    assert canvas.mode == "RGBA"
    assert canvas.size == (1280, 720)
    assert canvas.getpixel((0, 0)) == (0, 0, 0, 0)


def test_save_frame(tmp_path):
    renderer = FrameRenderer(
        width=1280,
        height=720,
    )

    frame = renderer.create_canvas()

    output_path = tmp_path / "frame.png"

    renderer.save_frame(
        image=frame,
        output_path=output_path,
    )

    assert output_path.exists()

    saved = Image.open(output_path)

    assert saved.mode == "RGBA"
    assert saved.size == (1280, 720)


def test_render_sequence(tmp_path):
    renderer = FrameRenderer(
        width=1280,
        height=720,
    )

    frames = [
        renderer.create_canvas()
        for _ in range(3)
    ]

    output_dir = tmp_path / "frames"

    frame_count = renderer.render_sequence(
        frames=frames,
        output_dir=output_dir,
    )

    assert frame_count == 3

    assert len(list(output_dir.glob("*.png"))) == 3
