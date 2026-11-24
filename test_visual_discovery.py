"""Test script for Phase 2: Visual Reverse Footage Discovery & Alignment."""

import sys
from pathlib import Path
from shorts_studio.discovery.pipeline import discover_visual_footage


def main():
    timeline_path = "cache/test_reference/timeline.json"
    reference_video = r"D:\sources\ai tantrum.mp4"
    
    if len(sys.argv) > 1:
        reference_video = sys.argv[1]
    if len(sys.argv) > 2:
        timeline_path = sys.argv[2]
        
    print(f"Running Phase 2 Visual Discovery on: {reference_video}\n", flush=True)
    result = discover_visual_footage(
        timeline_path=timeline_path,
        reference_video_path=reference_video,
        output_dir="cache/test_visual_discovery",
        max_search_candidates=2,
        similarity_threshold=0.68
    )
    
    print("\n--- FINAL SCENE ALIGNMENT REPORT ---")
    for s in result.scenes:
        print(f"\nScene {s.scene_id} ({s.target_duration}s: {s.reference_start_time}s -> {s.reference_end_time}s)")
        print(f"  Visual Query: {s.visual_query}")
        print(f"  Keyframes Saved: {len(s.keyframes)}")
        if s.status == "matched" and s.match:
            print(f"  STATUS: [MATCHED]")
            print(f"    Source Video: {s.match.video_title}")
            print(f"    URL: {s.match.video_url}")
            print(f"    Exact Range: {s.match.source_start_time}s -> {s.match.source_end_time}s")
            print(f"    Confidence: {s.match.match_confidence * 100:.1f}%")
        else:
            print(f"  STATUS: [NOT FOUND] (No matching source clip verified)")


if __name__ == "__main__":
    main()
