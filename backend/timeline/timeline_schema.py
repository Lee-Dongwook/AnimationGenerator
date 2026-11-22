from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from backend.scenes.scene_schema import EngineType


class TimelineTrackType(str, Enum):
    CHARACTER = "character"
    BACKGROUND = "background"
    CAMERA = "camera"
    AUDIO = "audio"


class TimelineClipType(str, Enum):
    ACTION = "action"
    BACKGROUND = "background"
    CAMERA = "camera"
    AUDIO = "audio"


class TimelineClip(BaseModel):
    id: str

    track_id: str
    target_id: str

    clip_type: TimelineClipType

    start: float = Field(ge=0)
    duration: float = Field(gt=0)

    engine: EngineType | None = None
    action_name: str | None = None

    asset_path: Path | None = None

    params: dict = Field(default_factory=dict)

    @property
    def end(self) -> float:
        return self.start + self.duration


class TimelineTrack(BaseModel):
    id: str
    track_type: TimelineTrackType
    target_id: str

    clips: list[TimelineClip] = Field(default_factory=list)


class TimelineSpec(BaseModel):
    scene_id: str

    duration: float = Field(gt=0)
    fps: int = Field(default=24, gt=0)

    width: int = Field(default=1280, gt=0)
    height: int = Field(default=720, gt=0)

    tracks: list[TimelineTrack] = Field(default_factory=list)
    clips: list[TimelineClip] = Field(default_factory=list)
