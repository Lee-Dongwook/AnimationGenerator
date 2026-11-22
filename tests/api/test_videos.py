from fastapi.testclient import TestClient

from backend.api.routes import videos
from backend.main import app


def test_generate_returns_browser_video_url(tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    monkeypatch.setattr(videos, "INPUT_DIR", input_dir)
    monkeypatch.setattr(videos, "OUTPUT_DIR", output_dir)

    def generate(_self, image_path, output_path, options):
        del image_path, options
        output_path.write_bytes(b"video")
        return output_path

    monkeypatch.setattr(videos.MotionEngine, "generate", generate)

    response = TestClient(app).post(
        "/videos/generate",
        files={"file": ("picture.png", b"image", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["video_url"] == f"/assets/output/{body['job_id']}.mp4"
    assert not list(input_dir.iterdir())
