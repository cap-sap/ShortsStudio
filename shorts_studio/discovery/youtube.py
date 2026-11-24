"""YouTube footage discovery using yt-dlp."""

import json
import subprocess
from pathlib import Path
from typing import List, Optional

from shorts_studio.utils.ffmpeg import find_binary
from shorts_studio.discovery.models import FootageCandidate


def search_youtube_shorts(query: str, max_results: int = 3) -> List[FootageCandidate]:
    """
    Searches YouTube for vertical short videos matching query without downloading media.
    Fetches titles, URLs, durations, thumbnails, and views via yt-dlp metadata extraction.
    """
    ytdlp_bin = find_binary("yt-dlp")
    search_term = f"ytsearch{max_results}:{query}"
    
    cmd = [
        ytdlp_bin,
        "--dump-json",
        "--flat-playlist",
        "--no-download",
        "--no-warnings",
        "--ignore-errors",
        search_term
    ]
    
    candidates: List[FootageCandidate] = []
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                video_id = data.get("id") or ""
                url = data.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}"
                title = data.get("title") or "Untitled Video"
                duration = float(data.get("duration") or 0.0)
                thumbnails_list = data.get("thumbnails", [])
                thumbnail = data.get("thumbnail") or (thumbnails_list[-1].get("url") if thumbnails_list else None)
                uploader = data.get("uploader") or data.get("channel") or None
                view_count = data.get("view_count")
                
                candidates.append(FootageCandidate(
                    candidate_id=video_id,
                    platform="youtube",
                    title=title,
                    url=url,
                    duration_seconds=round(duration, 2),
                    thumbnail_url=thumbnail,
                    channel_or_author=uploader,
                    view_count=view_count
                ))
            except json.JSONDecodeError:
                continue
    except subprocess.CalledProcessError as e:
        print(f"[!] Warning: yt-dlp search returned error for query '{query}': {e.stderr}")
        
    return candidates


def download_candidate(candidate: FootageCandidate, output_dir: Path, filename_prefix: str = "") -> str:
    """
    Downloads an individual candidate video to a local directory for editing.
    """
    ytdlp_bin = find_binary("yt-dlp")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prefix = f"{filename_prefix}_" if filename_prefix else ""
    target_template = str(output_dir / f"{prefix}{candidate.candidate_id}.%(ext)s")
    
    cmd = [
        ytdlp_bin,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", target_template,
        candidate.url
    ]
    
    subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True
    )
    
    # Locate downloaded file
    matches = list(output_dir.glob(f"{prefix}{candidate.candidate_id}.*"))
    if not matches:
        raise FileNotFoundError(f"Failed to locate downloaded candidate {candidate.candidate_id}")
        
    candidate.local_file_path = str(matches[0])
    return str(matches[0])
