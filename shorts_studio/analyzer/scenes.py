"""Scene and cut detection using PySceneDetect."""

from typing import List
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector, AdaptiveDetector

from shorts_studio.analyzer.models import SceneCut


def detect_scenes(proxy_video_path: str, threshold: float = 27.0, min_scene_len_frames: int = 15) -> List[SceneCut]:
    """
    Detects scene cuts on the proxy video.
    Returns a list of SceneCut objects with exact start/end timestamps and durations.
    """
    print(f"[*] Analyzing scene cuts on proxy video: {proxy_video_path}")
    video = open_video(str(proxy_video_path))
    scene_manager = SceneManager()
    
    # ContentDetector computes HSV color histogram differences across consecutive frames
    scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len_frames))
    
    scene_manager.detect_scenes(video=video)
    scene_list = scene_manager.get_scene_list()
    
    cuts: List[SceneCut] = []
    
    # If no cut detected (single continuous shot), consider whole video as scene 1
    if not scene_list:
        duration = video.duration.get_seconds()
        total_frames = video.duration.get_frames()
        cuts.append(SceneCut(
            scene_id=1,
            start_time=0.0,
            end_time=round(duration, 3),
            duration=round(duration, 3),
            start_frame=0,
            end_frame=total_frames
        ))
        return cuts
        
    for idx, (start_time, end_time) in enumerate(scene_list, start=1):
        start_sec = round(start_time.get_seconds(), 3)
        end_sec = round(end_time.get_seconds(), 3)
        duration = round(end_sec - start_sec, 3)
        
        cuts.append(SceneCut(
            scene_id=idx,
            start_time=start_sec,
            end_time=end_sec,
            duration=duration,
            start_frame=start_time.get_frames(),
            end_frame=end_time.get_frames()
        ))
        
    print(f"[✓] Detected {len(cuts)} scenes/cuts.")
    return cuts
