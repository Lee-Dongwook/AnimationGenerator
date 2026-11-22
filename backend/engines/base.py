from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from backend.scenes.scene_schema import EngineType

class ArtifactType(str, Enum):
    VIDEO = "video"
    IMAGE_SEQUENCE = "image_sequence"
    IMAGE = "image"

@dataclass
class EngineRequest:
    scene_id: str
    character_id: str

    engine_type: EngineType
    action_name: str

    image_path: Path
    output_path: Path

    duration: float
    fps: int

    width: int
    height: int

    params: dict[str, Any] = field(default_factory=dict)

@dataclass
class EngineResult:
    output_path: Path

    artifact_type: ArtifactType
    media_type: str

    duration: float
    fps: int

    frame_count: int

    has_alpha: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

class AnimationEngine(ABC):

    @property
    @abstractmethod
    def engine_type(self) -> EngineType:
        raise NotImplementedError

    @abstractmethod
    def render(
        self,
        request: EngineRequest,
    ) -> EngineResult:
        raise NotImplementedError

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
