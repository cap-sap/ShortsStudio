"""Data models for candidate source footage discovery."""

from typing import List, Optional
from pydantic import BaseModel, Field


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


class SceneCandidates(BaseModel):
    """List of candidate video clips discovered for an individual scene."""
    scene_id: int
    target_duration: float
    start_time: float
    end_time: float
    spoken_text: str = ""
    search_query: str
    candidates: List[FootageCandidate] = Field(default_factory=list)
    selected_candidate_id: Optional[str] = None


class DiscoveryResult(BaseModel):
    """Complete collection of discovered candidate footage across all scenes."""
    source_timeline: str
    total_scenes: int
    scene_matches: List[SceneCandidates] = Field(default_factory=list)

    def to_json_file(self, file_path: str):
        """Saves discovery result to a formatted JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_json_file(cls, file_path: str) -> "DiscoveryResult":
        """Loads discovery result from a JSON file."""
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
