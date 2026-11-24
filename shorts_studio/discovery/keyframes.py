"""Extracts sharp representative keyframes from reference video scenes."""

import cv2
from pathlib import Path
from typing import List

from shorts_studio.analyzer.models import SceneCut
from shorts_studio.discovery.models import KeyframeInfo


def extract_scene_keyframes(
    video_path: str,
    scene: SceneCut,
    output_dir: Path,
    frames_per_scene: int = 3
) -> List[KeyframeInfo]:
    """
    Extracts high-quality representative keyframe images from a specific scene cut.
    Samples frames evenly across the scene duration (e.g., at 25%, 50%, 75%).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    
    keyframe_infos: List[KeyframeInfo] = []
    
    # Calculate sample timestamps within scene interval
    duration = scene.duration
    start = scene.start_time
    
    if frames_per_scene == 1:
        percentages = [0.5]
    elif frames_per_scene == 2:
        percentages = [0.33, 0.66]
    else:
        percentages = [0.25, 0.50, 0.75]
        
    for idx, p in enumerate(percentages, start=1):
        target_time = round(start + (p * duration), 3)
        target_frame = int(target_time * fps)
        
        if total_frames > 0 and target_frame >= total_frames:
            target_frame = total_frames - 1
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if not ret or frame is None:
            continue
            
        filename = f"scene_{scene.scene_id:02d}_frame_{idx:02d}.jpg"
        save_path = output_dir / filename
        cv2.imwrite(str(save_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
        
        keyframe_infos.append(KeyframeInfo(
            frame_index=target_frame,
            timestamp=target_time,
            file_path=str(save_path)
        ))
        
    cap.release()
    return keyframe_infos
