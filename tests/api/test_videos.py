from types import SimpleNamespace

import pytest
from fastapi import HTTPException
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


def test_coverr_downloads_short_video_when_no_vertical_result_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(videos, "DOWNLOAD_DIR", tmp_path)
    monkeypatch.setattr(videos, "Settings", lambda: SimpleNamespace(coverr_api_key="key"))

    class Response:
        def __init__(self, body, content_type="application/json"):
            self.body = body
            self.headers = {"Content-Type": content_type}

        def read(self, _size=-1):
            body, self.body = self.body, b""
            return body

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    calls = []

    def open_url(request, timeout):
        method = request.get_method()
        calls.append((request.full_url, method, timeout))
        if method == "PATCH":
            return Response(b"", "")
        if request.full_url.startswith(videos.COVERR_API_URL):
            return Response(
                b'{"hits":[{"id":"short","title":"Forest Short","duration":"10","is_vertical":false,"urls":{"mp4_download":"https://download/short"}},{"id":"ideal","title":"Forest Ideal","duration":"16","is_vertical":false,"urls":{"mp4_download":"https://download/ideal"}}]}'
            )
        return Response(b"mp4-data", "video/mp4")

    monkeypatch.setattr(videos, "urlopen", open_url)

    response = TestClient(app).post("/videos/coverr/download", data={"query": "forest"})

    assert response.status_code == 200
    body = response.json()
    assert body["video_id"] == "ideal"
    assert body["video_url"].startswith("/assets/downloads/coverr-")
    assert len(calls) == 3
    assert calls[-1][1] == "PATCH"
    assert (tmp_path / body["video_url"].split("/")[-1]).read_bytes() == b"mp4-data"


def test_coverr_rejects_unrelated_search_results(monkeypatch):
    monkeypatch.setattr(videos, "Settings", lambda: SimpleNamespace(coverr_api_key="key"))
    monkeypatch.setattr(
        videos,
        "coverr_request",
        lambda *_args, **_kwargs: b'{"hits":[{"id":"snow","title":"Snow falling","urls":{"mp4_download":"https://download/snow"}}]}',
    )

    with pytest.raises(HTTPException, match="No relevant downloadable Coverr video"):
        videos.download_coverr_video("funny fails")
