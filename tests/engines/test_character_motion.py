from PIL import Image

from backend.engines.base import (
    ArtifactType,
    EngineRequest,
)
from backend.engines.character_motion import CharacterMotionEngine
from backend.scenes.scene_schema import EngineType


def test_render_character_frames(tmp_path):

    character_path = tmp_path / "rabbit.png"

    Image.new(
        "RGBA",
        (200, 200),
        (255, 0, 0, 255),
    ).save(character_path)

    output_path = tmp_path / "frames"

    request = EngineRequest(
        scene_id="test_scene",
        character_id="rabbit",
        engine_type=EngineType.TRANSFORM,
        action_name="bounce",
        image_path=character_path,
        output_path=output_path,
        duration=2,
        fps=24,
        width=1280,
        height=720,
        params={
            "preset": "bounce",
        },
    )

    engine = CharacterMotionEngine()

    result = engine.render(request)

    assert result.artifact_type == ArtifactType.IMAGE_SEQUENCE
    assert result.has_alpha is True
    assert result.frame_count == 48

    frames = sorted(
        output_path.glob("*.png")
    )

    assert len(frames) == 48

    first_frame = Image.open(frames[0])

    assert first_frame.mode == "RGBA"
    assert first_frame.size == (1280, 720)

    assert first_frame.getpixel((0, 0))[3] == 0


def test_generate_character_video(tmp_path):
    character_path = tmp_path / "character.png"
    Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(character_path)

    output_path = tmp_path / "character.mp4"

    result = CharacterMotionEngine().generate(
        character_path=character_path,
        background_path=None,
        output_path=output_path,
        options={
            "width": 64,
            "height": 64,
            "fps": 2,
            "duration": 1,
            "preset": "bounce",
        },
    )

    assert result == output_path
    assert output_path.is_file()
    assert output_path.stat().st_size > 0
