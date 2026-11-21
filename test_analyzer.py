"""Test script to run the Phase 1 Reference Video Analyzer."""

import sys
from pathlib import Path
from shorts_studio.analyzer.pipeline import analyze_reference_video


def main():
    # Allow passing custom video path or URL, or fall back to local test clip
    if len(sys.argv) > 1:
        test_source = sys.argv[1]
    else:
        fallback_candidates = [
            r"D:\sources\ai tantrum.mp4",
            r"D:\sources\short_video.mp4"
        ]
        test_source = None
        for candidate in fallback_candidates:
            if Path(candidate).exists():
                test_source = candidate
                break
                
        if not test_source:
            print("Error: No test video found. Please pass a video path: python test_analyzer.py <path_to_video>")
            sys.exit(1)
            
    print(f"Running Phase 1 Test with: {test_source}\n")
    timeline = analyze_reference_video(test_source, output_dir="cache/test_reference")
    
    print("\n--- SAMPLE SCENES DETECTED ---")
    for s in timeline.scenes[:5]:
        print(f"  Scene {s.scene_id}: {s.start_time}s -> {s.end_time}s (Duration: {s.duration}s)")
        
    print("\n--- SAMPLE WORDS TRANSCRIBED ---")
    for w in timeline.words[:10]:
        print(f"  [{w.start_time}s - {w.end_time}s] '{w.word}' (prob: {w.probability})")
        
    print("\n--- SAMPLE AUDIO CUES ---")
    for a in timeline.audio_cues[:5]:
        print(f"  At {a.timestamp}s: {a.cue_type} (intensity: {a.intensity})")


if __name__ == "__main__":
    main()
