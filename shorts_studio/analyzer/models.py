"""Pydantic data models defining the declarative Timeline schema."""

from typing import List, Optional
from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """Individual spoken word with millisecond-precision timestamps."""
    word: str
    start_time: float = Field(..., description="Start timestamp in seconds")
    end_time: float = Field(..., description="End timestamp in seconds")
    probability: Optional[float] = Field(None, description="Confidence score from 0.0 to 1.0")


class SceneCut(BaseModel):
    """An individual scene interval detected in the reference video."""
    scene_id: int
    start_time: float = Field(..., description="Start timestamp in seconds")
    end_time: float = Field(..., description="End timestamp in seconds")
    duration: float = Field(..., description="Duration of this scene in seconds")
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None


class AudioCue(BaseModel):
    """Audio beat or energy spike for pacing cuts to music/sound."""
    timestamp: float
    cue_type: str = Field("beat", description="Type of cue: 'beat', 'energy_spike', or 'silence'")
    intensity: float = Field(1.0, description="Normalized intensity 0.0 to 1.0")


class VideoMetadata(BaseModel):
    """Metadata describing the reference video."""
    source_path_or_url: str
    duration_seconds: float
    fps: float
    width: int
    height: int
    aspect_ratio: str = "9:16"


class VideoTimeline(BaseModel):
    """The complete editing blueprint for recreating the reference video."""
    metadata: VideoMetadata
    scenes: List[SceneCut] = Field(default_factory=list)
    words: List[WordTimestamp] = Field(default_factory=list)
    audio_cues: List[AudioCue] = Field(default_factory=list)

    def to_json_file(self, file_path: str):
        """Export timeline to formatted JSON file."""
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
