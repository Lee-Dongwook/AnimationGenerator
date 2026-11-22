from abc import ABC, abstractmethod
from pathlib import Path


class VideoGenerationEngine(ABC):

    @abstractmethod
    def generate(
        self,
        image_path: Path,
        output_path: Path,
        options: dict,
    ) -> Path:
        """Generate an animated video from an image."""
        raise NotImplementedError
