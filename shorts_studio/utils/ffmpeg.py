"""FFmpeg and FFprobe utility helpers."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def find_binary(binary_name: str) -> str:
    """Finds binary in system PATH or known local fallback directories."""
    path = shutil.which(binary_name)
    if path:
        return path
    
    # Check fallback folder D:\yt-dpl
    fallback = Path(r"D:\yt-dpl") / f"{binary_name}.exe"
    if fallback.exists():
        return str(fallback)
        
    raise FileNotFoundError(f"Binary '{binary_name}' was not found in PATH or D:\\yt-dpl.")


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Extracts resolution, duration, and framerate using ffprobe."""
    ffprobe_bin = find_binary("ffprobe")
    cmd = [
        ffprobe_bin,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration:format=duration",
        "-of", "json",
        str(video_path)
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    data = json.loads(result.stdout)
    
    stream = data.get("streams", [{}])[0]
    fmt = data.get("format", {})
    
    width = int(stream.get("width", 1080))
    height = int(stream.get("height", 1920))
    
    # Calculate FPS from fraction like "30/1" or "60000/1001"
    fps_raw = stream.get("r_frame_rate", "30/1")
    if "/" in fps_raw:
        num, den = fps_raw.split("/")
        fps = float(num) / float(den) if float(den) != 0 else 30.0
    else:
        fps = float(fps_raw)
        
    duration = float(stream.get("duration") or fmt.get("duration") or 0.0)
    
    return {
        "width": width,
        "height": height,
        "fps": round(fps, 3),
        "duration": round(duration, 3)
    }


def create_proxy(input_path: str, output_proxy_path: str, target_height: int = 640) -> str:
    """
    Creates a fast, lightweight low-resolution proxy (e.g. 360x640)
    using veryfast preset to minimize CPU usage.
    """
    ffmpeg_bin = find_binary("ffmpeg")
    output_path = Path(output_proxy_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-vf", f"scale=-2:{target_height}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "28",
        "-an",  # strip audio for pure visual proxy
        str(output_path)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return str(output_path)


def extract_audio_wav(input_path: str, output_wav_path: str) -> str:
    """
    Extracts a 16kHz mono WAV audio track optimal for Whisper speech recognition
    and audio rhythm analysis.
    """
    ffmpeg_bin = find_binary("ffmpeg")
    output_path = Path(output_wav_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_path)
    ]
    
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return str(output_path)
