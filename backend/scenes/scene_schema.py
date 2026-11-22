from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class EngineType(str, Enum):
    TRANSFORM = "transform"
    POSE = "pose"
    AI_VIDEO = "ai_video"


class ActionSpec(BaseModel):
    engine: EngineType
    name: str

    duration: float = Field(gt=0)
    repeat: int = Field(default=1, ge=1)

    params: dict[str, Any] = Field(default_factory=dict)


class CharacterSpec(BaseModel):
    id: str
    asset_path: Path

    actions: list[ActionSpec]


class SceneSpec(BaseModel):
    scene_id: str

    width: int = Field(default=1280, gt=0)
    height: int = Field(default=720, gt=0)
    fps: int = Field(default=24, gt=0)

    duration: float = Field(gt=0)

    background: str | None = None

    characters: list[CharacterSpec]
