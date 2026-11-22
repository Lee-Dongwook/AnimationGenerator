
import json
import re
import uuid

from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, File, HTTPException, UploadFile, Form
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.engines.motion_engine import MotionEngine
from backend.engines.character_motion import CharacterMotionEngine


router = APIRouter(prefix="/videos", tags=["Videos"])

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "assets" / "input"
OUTPUT_DIR = BASE_DIR / "assets" / "output"
DOWNLOAD_DIR = BASE_DIR / "assets" / "downloads"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
COVERR_API_URL = "https://api.coverr.co"
MAX_COVERR_VIDEO_BYTES = 100 * 1024 * 1024


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    coverr_api_key: str = ""


def coverr_request(path: str, api_key: str, *, method: str = "GET") -> bytes:
    request = Request(
        f"{COVERR_API_URL}{path}",
        headers={"x-api-key": api_key},
        method=method,
    )

    with urlopen(request, timeout=30) as response:
        return response.read()


def download_coverr_video(query: str) -> tuple[Path, dict]:
    api_key = Settings().coverr_api_key

    if not api_key:
        raise HTTPException(status_code=500, detail="COVERR_API_KEY is not configured.")

    search = urlencode({"query": query, "page_size": 20, "urls": "true"})

    try:
        results = json.loads(
            coverr_request(f"/videos?{search}", api_key).decode("utf-8")
        )
        terms = re.findall(r"\w+", query.lower())
        downloadable = [
            item
            for item in results.get("hits", [])
            if item.get("urls", {}).get("mp4_download")
        ]
        relevant = [
            item
            for item in downloadable
            if all(
                term in " ".join(
                    str(value)
                    for value in [
                        item.get("title", ""),
                        item.get("description", ""),
                        *item.get("tags", []),
                    ]
                ).lower()
                for term in terms
            )
        ]
        candidates = [item for item in relevant if item.get("is_vertical")]
        candidates = candidates or relevant
        video = next(
            (
                item
                for item in candidates
                if 15 <= float(item.get("duration", 0)) <= 20
            ),
            next(iter(candidates), None),
        )

        if not video:
            raise HTTPException(
                status_code=404,
                detail="No relevant downloadable Coverr video found.",
            )

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DOWNLOAD_DIR / f"coverr-{uuid.uuid4()}.mp4"
        download_request = Request(video["urls"]["mp4_download"])

        with urlopen(download_request, timeout=60) as response, output_path.open("wb") as file:
            content_type = response.headers.get("Content-Type", "")
            if content_type and not content_type.startswith("video/"):
                raise ValueError("Coverr returned a non-video file.")

            downloaded = 0
            while chunk := response.read(1024 * 1024):
                downloaded += len(chunk)
                if downloaded > MAX_COVERR_VIDEO_BYTES:
                    raise ValueError("Coverr video exceeds the 100 MB limit.")
                file.write(chunk)

        if not output_path.stat().st_size:
            raise ValueError("Coverr returned an empty video file.")

        coverr_request(f"/videos/{video['id']}/stats/downloads", api_key, method="PATCH")
        return output_path, video

    except HTTPException:
        raise
    except Exception as error:
        if "output_path" in locals():
            output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=502, detail="Could not download Coverr video.") from error


@router.post("/coverr/download")
async def download_coverr_stock_video(query: str = Form(...)):
    normalized_query = query.strip()

    if not normalized_query:
        raise HTTPException(status_code=400, detail="Search query is required.")

    output_path, video = download_coverr_video(normalized_query)
    return {
        "status": "completed",
        "video_id": video["id"],
        "title": video.get("title", "Coverr video"),
        "duration": video.get("duration"),
        "video_path": str(output_path),
        "video_url": f"/assets/downloads/{output_path.name}",
        "source": {"name": "Coverr", "url": "https://coverr.co"},
    }


@router.post("/generate")
async def generate_video(
    file: UploadFile = File(...),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format.",
        )

    job_id = str(uuid.uuid4())

    input_path = INPUT_DIR / f"{job_id}{extension}"
    output_path = OUTPUT_DIR / f"{job_id}.mp4"

    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Empty image file.",
            )

        input_path.write_bytes(content)

        engine = MotionEngine()

        result = engine.generate(
            image_path=input_path,
            output_path=output_path,
            options={
                "width": 1280,
                "height": 720,
                "fps": 24,
                "duration": 5,
                "zoom_strength": 0.15,
            },
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "video_path": str(result),
            "video_url": f"/assets/output/{output_path.name}",
        }

    except HTTPException:
        raise

    except Exception as error:
        output_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        input_path.unlink(missing_ok=True)
        await file.close()

@router.post("/character/generate")
async def generate_character_video(
    character: UploadFile = File(...),
    background: UploadFile | None = File(None),
    preset: str = Form("bounce"),
):
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    allowed_presets = {"bounce", "wave", "sway", "dance"}

    character_ext = Path(character.filename or "").suffix.lower()

    if character_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported character image format.",
        )

    if preset not in allowed_presets:
        raise HTTPException(
            status_code=400,
            detail="Unsupported motion preset.",
        )

    background_ext = None

    if background:
        background_ext = Path(background.filename or "").suffix.lower()

        if background_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Unsupported background image format.",
            )

    job_id = str(uuid.uuid4())

    character_path = INPUT_DIR / f"{job_id}_character{character_ext}"
    background_path = (
        INPUT_DIR / f"{job_id}_background{background_ext}"
        if background and background_ext
        else None
    )

    output_path = OUTPUT_DIR / f"{job_id}.mp4"

    try:
        character_data = await character.read()

        if not character_data:
            raise HTTPException(
                status_code=400,
                detail="Empty character image.",
            )

        character_path.write_bytes(character_data)

        if background and background_path:
            background_data = await background.read()

            if not background_data:
                raise HTTPException(
                    status_code=400,
                    detail="Empty background image.",
                )

            background_path.write_bytes(background_data)

        engine = CharacterMotionEngine()

        result = engine.generate(
            character_path=character_path,
            background_path=background_path,
            output_path=output_path,
            options={
                "width": 1280,
                "height": 720,
                "fps": 24,
                "duration": 5,
                "preset": preset,
            },
        )

        return {
            "job_id": job_id,
            "status": "completed",
            "preset": preset,
            "video_path": str(result),
            "video_url": f"/assets/output/{output_path.name}",
        }

    except HTTPException:
        output_path.unlink(missing_ok=True)
        raise

    except Exception as error:
        output_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    finally:
        character_path.unlink(missing_ok=True)

        if background_path:
            background_path.unlink(missing_ok=True)

        await character.close()

        if background:
            await background.close()
