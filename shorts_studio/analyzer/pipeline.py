"""Orchestrates Phase 1: Reference Video Ingestion -> Analysis -> Master Timeline JSON."""

from pathlib import Path
from typing import Optional

from shorts_studio.analyzer.models import VideoTimeline
from shorts_studio.analyzer.ingest import ingest_reference_video
from shorts_studio.analyzer.scenes import detect_scenes
from shorts_studio.analyzer.transcribe import transcribe_audio
from shorts_studio.analyzer.audio import analyze_audio_energy


def analyze_reference_video(
    source: str,
    output_dir: str = "cache/reference",
    whisper_model: str = "base"
) -> VideoTimeline:
    """
    Complete Phase 1 pipeline:
    1. Ingests video (URL or local) & creates 360p proxy + 16kHz WAV
    2. Detects exact scene cuts
    3. Transcribes spoken words with millisecond timestamps
    4. Detects rhythmic audio energy peaks
    5. Saves and returns the unified VideoTimeline JSON blueprint
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print(f"SHORTSSTUDIO: ANALYZING REFERENCE VIDEO")
    print(f"Source: {source}")
    print("=" * 60)
    
    # 1. Ingestion & Proxy
    ingest_result = ingest_reference_video(source, work_dir=str(out_dir))
    
    # 2. Scene / Cut Detection
    scenes = detect_scenes(ingest_result.proxy_video_path)
    
    # 3. Speech Transcription
    words = transcribe_audio(ingest_result.audio_wav_path, model_size=whisper_model)
    
    # 4. Audio Dynamics
    audio_cues = analyze_audio_energy(ingest_result.audio_wav_path)
    
    # 5. Assemble Timeline
    timeline = VideoTimeline(
        metadata=ingest_result.metadata,
        scenes=scenes,
        words=words,
        audio_cues=audio_cues
    )
    
    timeline_path = out_dir / "timeline.json"
    timeline.to_json_file(str(timeline_path))
    
    print("=" * 60)
    print(f"[✓] PHASE 1 COMPLETE! Timeline saved to: {timeline_path}")
    print(f"    - Total Duration: {timeline.metadata.duration_seconds}s")
    print(f"    - Scenes/Cuts Detected: {len(timeline.scenes)}")
    print(f"    - Words Transcribed: {len(timeline.words)}")
    print(f"    - Audio Cues Found: {len(timeline.audio_cues)}")
    print("=" * 60)
    
    return timeline
