"""Video ingestion and proxy generation module."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple
from pydantic import BaseModel

from shorts_studio.utils.ffmpeg import get_video_info, create_proxy, extract_audio_wav, find_binary
from shorts_studio.analyzer.models import VideoMetadata


class IngestResult(BaseModel):
    """Holds artifacts and metadata produced during ingestion."""
    original_video_path: str
    proxy_video_path: str
    audio_wav_path: str
    metadata: VideoMetadata


def download_with_ytdlp(url: str, output_dir: Path) -> Path:
    """Downloads highest quality vertical short/reel using yt-dlp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target_template = str(output_dir / "original.%(ext)s")
    
    ytdlp_bin = find_binary("yt-dlp")
    cmd = [
        ytdlp_bin,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", target_template,
        url
    ]
    
    subprocess.run(cmd, check=True)
    
    # Locate the downloaded file
    downloaded_files = list(output_dir.glob("original.*"))
    if not downloaded_files:
        raise FileNotFoundError(f"Failed to find downloaded file in {output_dir}")
        
    return downloaded_files[0]


def ingest_reference_video(source: str, work_dir: str = "cache/reference") -> IngestResult:
    """
    Ingests a reference video from local file or web URL, extracts metadata,
    and produces a fast 360p proxy and clean 16kHz audio track.
    """
    base_dir = Path(work_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    is_url = source.startswith("http://") or source.startswith("https://")
    
    if is_url:
        print(f"[*] Downloading reference video from URL: {source}")
        video_path = download_with_ytdlp(source, base_dir)
    else:
        src_path = Path(source)
        if not src_path.exists():
            raise FileNotFoundError(f"Local video file not found: {source}")
        video_path = src_path
        
    print(f"[*] Reading video metadata: {video_path}")
    info = get_video_info(str(video_path))
    
    metadata = VideoMetadata(
        source_path_or_url=str(source),
        duration_seconds=info["duration"],
        fps=info["fps"],
        width=info["width"],
        height=info["height"],
        aspect_ratio="9:16" if info["height"] > info["width"] else "16:9"
    )
    
    # Generate 360p Proxy
    proxy_path = base_dir / "proxy_360p.mp4"
    print(f"[*] Generating fast 360p proxy video at: {proxy_path}")
    create_proxy(str(video_path), str(proxy_path), target_height=640)
    
    # Extract Audio WAV
    audio_path = base_dir / "audio_16k.wav"
    print(f"[*] Extracting 16kHz mono WAV audio at: {audio_path}")
    extract_audio_wav(str(video_path), str(audio_path))
    
    return IngestResult(
        original_video_path=str(video_path),
        proxy_video_path=str(proxy_path),
        audio_wav_path=str(audio_path),
        metadata=metadata
    )
