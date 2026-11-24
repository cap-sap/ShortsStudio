"""Orchestrator for Phase 2: Timeline -> Semantic Queries -> Video Search -> Candidates JSON."""

import json
from pathlib import Path
from typing import Optional

from shorts_studio.analyzer.models import VideoTimeline
from shorts_studio.discovery.models import DiscoveryResult, SceneCandidates
from shorts_studio.discovery.query_gen import generate_scene_query
from shorts_studio.discovery.youtube import search_youtube_shorts


def discover_source_footage(
    timeline_path: str,
    output_json_path: str = "cache/candidates.json",
    candidates_per_scene: int = 3
) -> DiscoveryResult:
    """
    Takes a timeline.json from Phase 1, extracts search queries for each scene cut,
    searches for matching candidate clips, and exports candidates.json for Phase 3 review.
    """
    timeline_file = Path(timeline_path)
    if not timeline_file.exists():
        raise FileNotFoundError(f"Timeline file not found: {timeline_path}")
        
    print("=" * 60)
    print("SHORTSSTUDIO: PHASE 2 - SOURCE FOOTAGE DISCOVERY")
    print(f"Reading Timeline: {timeline_path}")
    print("=" * 60)
    
    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
    timeline = VideoTimeline(**timeline_data)
    
    scene_matches = []
    
    for scene in timeline.scenes:
        spoken_text, search_query = generate_scene_query(scene, timeline.words)
        print(f"\n[*] Scene {scene.scene_id} ({scene.duration}s):")
        print(f"    Spoken Text : '{spoken_text}'")
        print(f"    Search Query: '{search_query}'")
        print(f"    Searching YouTube Shorts...")
        
        candidates = search_youtube_shorts(search_query, max_results=candidates_per_scene)
        print(f"    [✓] Found {len(candidates)} candidates.")
        for idx, c in enumerate(candidates, start=1):
            print(f"        {idx}. {c.title[:50]}... ({c.duration_seconds}s) [{c.url}]")
            
        scene_candidates = SceneCandidates(
            scene_id=scene.scene_id,
            target_duration=scene.duration,
            start_time=scene.start_time,
            end_time=scene.end_time,
            spoken_text=spoken_text,
            search_query=search_query,
            candidates=candidates,
            selected_candidate_id=candidates[0].candidate_id if candidates else None
        )
        scene_matches.append(scene_candidates)
        
    result = DiscoveryResult(
        source_timeline=str(timeline_path),
        total_scenes=len(scene_matches),
        scene_matches=scene_matches
    )
    
    out_file = Path(output_json_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    result.to_json_file(str(out_file))
    
    print("\n" + "=" * 60)
    print(f"[✓] PHASE 2 COMPLETE! Discovered candidates saved to: {out_file}")
    print(f"    - Total Scenes Processed: {result.total_scenes}")
    total_candidates = sum(len(s.candidates) for s in result.scene_matches)
    print(f"    - Total Candidate Clips Found: {total_candidates}")
    print("=" * 60)
    
    return result
