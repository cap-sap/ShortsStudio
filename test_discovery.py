"""Test script for Phase 2: Source Footage Discovery."""

import sys
from pathlib import Path
from shorts_studio.discovery.pipeline import discover_source_footage


def main():
    timeline_path = sys.argv[1] if len(sys.argv) > 1 else "cache/test_reference/timeline.json"
    
    if not Path(timeline_path).exists():
        print(f"Error: Timeline file '{timeline_path}' does not exist. Run test_analyzer.py first.")
        sys.exit(1)
        
    print(f"Testing Phase 2 with timeline: {timeline_path}\n")
    result = discover_source_footage(timeline_path, output_json_path="cache/test_candidates.json", candidates_per_scene=3)
    
    print("\n--- DISCOVERY SUMMARY ---")
    for s in result.scene_matches:
        print(f"\nScene {s.scene_id} ({s.target_duration}s) | Query: '{s.search_query}'")
        for i, c in enumerate(s.candidates, start=1):
            print(f"  [{i}] {c.title}")
            print(f"      Duration: {c.duration_seconds}s | Channel: {c.channel_or_author}")
            print(f"      URL: {c.url}")


if __name__ == "__main__":
    main()
