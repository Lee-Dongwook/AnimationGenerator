
import uuid

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, Form

from backend.engines.motion_engine import MotionEngine
from backend.engines.character_motion import CharacterMotionEngine


router = APIRouter(prefix="/videos", tags=["Videos"])

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_DIR = BASE_DIR / "assets" / "input"
OUTPUT_DIR = BASE_DIR / "assets" / "output"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


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
