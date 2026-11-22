
from pathlib import Path

from backend.engines.base import VideoGenerationEngine


class MotionEngine(VideoGenerationEngine):

    def generate(
        self,
        image_path: Path,
        output_path: Path,
        options: dict,
    ) -> Path:
        raise NotImplementedError(
            "Motion generation is not implemented yet."
        )
