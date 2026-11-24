"""Data models for visual keyframe extraction, reverse search, and timestamp alignment."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KeyframeInfo(BaseModel):
    """Metadata for an extracted reference keyframe."""
    frame_index: int
    timestamp: float
    file_path: str


class FootageCandidate(BaseModel):
    """An individual candidate clip found for a scene."""
    candidate_id: str
    platform: str = "youtube"
    title: str
    url: str
    duration_seconds: float = 0.0
    thumbnail_url: Optional[str] = None
    channel_or_author: Optional[str] = None
    view_count: Optional[int] = None
    local_file_path: Optional[str] = None


class VisualMatch(BaseModel):
    """The exact matched source footage and timestamp range."""
    video_url: str
    video_title: str
    source_start_time: float = Field(..., description="Start timestamp in source video (seconds)")
    source_end_time: float = Field(..., description="End timestamp in source video (seconds)")
    match_confidence: float = Field(..., description="Confidence score 0.0 to 1.0 (e.g. based on visual similarity)")
    source_duration: Optional[float] = None
    thumbnail_url: Optional[str] = None


class VisualSceneResult(BaseModel):
    """Discovery and alignment result for an individual scene."""
    scene_id: int
    target_duration: float
    reference_start_time: float
    reference_end_time: float
    keyframes: List[KeyframeInfo] = Field(default_factory=list)
    visual_query: str = Field(..., description="Visual search query generated from frames and scene context")
    status: str = Field("not_found", description="'matched' or 'not_found'")
    match: Optional[VisualMatch] = None
    candidate_urls_checked: List[str] = Field(default_factory=list)


class VisualDiscoveryResult(BaseModel):
    """Complete collection of visual footage discovery across all scenes."""
    source_timeline: str
    total_scenes: int
    matched_scenes_count: int = 0
    unmatched_scenes_count: int = 0
    scenes: List[VisualSceneResult] = Field(default_factory=list)

    def to_json_file(self, file_path: str):
        """Saves discovery result to formatted JSON file."""
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_json_file(cls, file_path: str) -> "VisualDiscoveryResult":
        """Loads discovery result from JSON file."""
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
