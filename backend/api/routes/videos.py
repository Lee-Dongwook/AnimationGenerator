
import uuid

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.engines.motion_engine import MotionEngine


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
