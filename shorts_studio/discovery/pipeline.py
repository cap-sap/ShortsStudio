"""Complete Phase 2 Pipeline: Keyframe Extraction -> Visual Search -> Video Alignment -> Status Report."""

import json
from pathlib import Path
from typing import Optional, List

from shorts_studio.analyzer.models import VideoTimeline
from shorts_studio.discovery.models import (
    VisualDiscoveryResult,
    VisualSceneResult,
    VisualMatch,
    KeyframeInfo
)
from shorts_studio.discovery.keyframes import extract_scene_keyframes
from shorts_studio.discovery.vision import generate_visual_search_query
from shorts_studio.discovery.youtube import search_youtube_shorts, download_candidate
from shorts_studio.discovery.matcher import scan_video_for_keyframe


def discover_visual_footage(
    timeline_path: str,
    reference_video_path: str,
    output_dir: str = "cache/visual_discovery",
    local_sources_dir: Optional[str] = None,
    max_search_candidates: int = 3,
    similarity_threshold: float = 0.70
) -> VisualDiscoveryResult:
    """
    Executes the human-editor video research workflow:
    1. Extracts sharp keyframes for each visual scene cut.
    2. Builds visual search queries to find full raw broadcasts/clips.
    3. Searches YouTube and checks local clips in local_sources_dir.
    4. Scans candidate videos frame-by-frame with perceptual hashing & histograms.
    5. Pinpoints the exact source_start_time and source_end_time for matched clips.
    6. Flags scenes with 'not_found' if no candidate matches.
    """
    base_out = Path(output_dir).resolve()
    keyframe_dir = (base_out / "keyframes").resolve()
    candidate_cache_dir = (base_out / "candidate_videos").resolve()
    base_out.mkdir(parents=True, exist_ok=True)
    keyframe_dir.mkdir(parents=True, exist_ok=True)
    candidate_cache_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 65)
    print("SHORTSSTUDIO: PHASE 2 - VISUAL REVERSE FOOTAGE DISCOVERY")
    print(f"Reference Video : {reference_video_path}")
    print(f"Reference Timeline : {timeline_path}")
    print("=" * 65)
    
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
    timeline = VideoTimeline(**timeline_data)
    
    scene_results: List[VisualSceneResult] = []
    matched_count = 0
    unmatched_count = 0
    
    # Gather potential local candidates if directory provided
    local_videos = []
    if local_sources_dir and Path(local_sources_dir).exists():
        for ext in ("*.mp4", "*.mkv", "*.mov", "*.webm"):
            local_videos.extend(list(Path(local_sources_dir).glob(ext)))
            
    for scene in timeline.scenes:
        print(f"\n" + "-" * 50)
        print(f"[*] Processing Scene {scene.scene_id} ({scene.duration}s: {scene.start_time}s -> {scene.end_time}s)")
        
        # 1. Extract Keyframes
        keyframes = extract_scene_keyframes(reference_video_path, scene, keyframe_dir, frames_per_scene=3)
        print(f"    [✓] Extracted {len(keyframes)} keyframes to: {keyframe_dir.name}/")
        
        # 2. Generate Visual Search Query
        visual_query = generate_visual_search_query(scene, keyframes, timeline.words)
        print(f"    [✓] Visual Query: '{visual_query}'")
        
        # 3. Candidate Search
        print(f"    [*] Searching YouTube for source videos...")
        yt_candidates = search_youtube_shorts(visual_query, max_results=max_search_candidates)
        print(f"    [✓] Found {len(yt_candidates)} candidate videos online.")
        
        scene_result = VisualSceneResult(
            scene_id=scene.scene_id,
            target_duration=scene.duration,
            reference_start_time=scene.start_time,
            reference_end_time=scene.end_time,
            keyframes=keyframes,
            visual_query=visual_query,
            status="not_found",
            match=None,
            candidate_urls_checked=[c.url for c in yt_candidates]
        )
        
        # 4. Visual Frame Matching
        # Primary reference frame is the midpoint keyframe
        primary_keyframe = keyframes[len(keyframes) // 2].file_path
        found_match = False
        
        # Scan discovered YouTube candidates
        for idx, candidate in enumerate(yt_candidates[:2], start=1):
            print(f"    [*] Checking candidate #{idx}: '{candidate.title[:45]}...' ({candidate.duration_seconds}s)", flush=True)
            try:
                downloaded_file = download_candidate(
                    candidate,
                    candidate_cache_dir,
                    filename_prefix=f"scene_{scene.scene_id}_c{idx}",
                    low_res=True
                )
                print(f"        Scanning frames to pinpoint exact match...", flush=True)
                match_coords = scan_video_for_keyframe(
                    candidate_video_path=downloaded_file,
                    reference_keyframe_path=primary_keyframe,
                    scene_duration=scene.duration,
                    similarity_threshold=similarity_threshold
                )
                
                if match_coords:
                    start_t, end_t, conf = match_coords
                    print(f"        [🎉 MATCH CONFIRMED!] Confidence: {conf * 100:.1f}%", flush=True)
                    print(f"        Exact Moment: {start_t}s -> {end_t}s in video", flush=True)
                    print(f"        URL: {candidate.url}", flush=True)
                    scene_result.status = "matched"
                    scene_result.match = VisualMatch(
                        video_url=candidate.url,
                        video_title=candidate.title,
                        source_start_time=start_t,
                        source_end_time=end_t,
                        match_confidence=conf,
                        source_duration=candidate.duration_seconds,
                        thumbnail_url=candidate.thumbnail_url
                    )
                    found_match = True
                    matched_count += 1
                    break
                else:
                    print(f"        [i] Clip #{idx} did not contain this exact visual moment.", flush=True)
            except Exception as e:
                print(f"        [!] Download or verification issue: {e}", flush=True)
                
        if not found_match:
            print(f"    [⚠️ NOT FOUND] No candidate video matched Scene {scene.scene_id}.")
            unmatched_count += 1
            
        scene_results.append(scene_result)
        
    result = VisualDiscoveryResult(
        source_timeline=str(timeline_path),
        total_scenes=len(scene_results),
        matched_scenes_count=matched_count,
        unmatched_scenes_count=unmatched_count,
        scenes=scene_results
    )
    
    out_file = base_out / "visual_candidates.json"
    result.to_json_file(str(out_file))
    
    print("\n" + "=" * 65)
    print(f"[✓] PHASE 2 VISUAL DISCOVERY COMPLETE!")
    print(f"    - Results saved to: {out_file}")
    print(f"    - Total Scenes : {result.total_scenes}")
    print(f"    - Matched      : {result.matched_scenes_count}")
    print(f"    - Not Found    : {result.unmatched_scenes_count}")
    print("=" * 65)
    
    return result
