"""Visual frame matcher using Perceptual Hashing (dHash) and OpenCV Color Histograms."""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List

from shorts_studio.discovery.models import KeyframeInfo, VisualMatch


def compute_dhash(image: np.ndarray, hash_size: int = 8) -> int:
    """
    Computes a 64-bit difference hash (dHash) for an image.
    Invariant to video scaling, slight color grading, and compression.
    """
    resized = cv2.resize(image, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    else:
        gray = resized
        
    diff = gray[:, 1:] > gray[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def compute_hsv_hist(image: np.ndarray) -> np.ndarray:
    """Computes a normalized 2D HSV color histogram."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist


def calculate_frame_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Combines Perceptual Hashing and HSV Histogram correlation to measure
    similarity between two video frames (0.0 = completely different, 1.0 = identical).
    """
    # 1. dHash distance (structural similarity)
    h1 = compute_dhash(img1)
    h2 = compute_dhash(img2)
    hamming_dist = bin(h1 ^ h2).count('1')
    hash_sim = max(0.0, 1.0 - (hamming_dist / 32.0))  # 32-bit tolerance scaling
    
    # 2. Color histogram correlation
    hist1 = compute_hsv_hist(img1)
    hist2 = compute_hsv_hist(img2)
    color_corr = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
    color_sim = max(0.0, color_corr)
    
    # Weighted combined similarity: 60% structure, 40% color
    combined = (0.60 * hash_sim) + (0.40 * color_sim)
    return round(float(combined), 3)


def scan_video_for_keyframe(
    candidate_video_path: str,
    reference_keyframe_path: str,
    scene_duration: float,
    sample_interval_sec: float = 0.5,
    similarity_threshold: float = 0.70
) -> Optional[Tuple[float, float, float]]:
    """
    Rapidly scans a candidate source video to locate where the reference keyframe appears.
    Uses cap.grab() to skip decoding non-sampled frames for high CPU throughput.
    Returns: (start_time, end_time, confidence) if matched, or None if not found.
    """
    ref_img = cv2.imread(str(reference_keyframe_path))
    if ref_img is None:
        raise FileNotFoundError(f"Could not load reference keyframe: {reference_keyframe_path}")
        
    cap = cv2.VideoCapture(str(candidate_video_path))
    if not cap.isOpened():
        return None
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    video_duration = total_frames / fps if fps > 0 else 0.0
    
    frame_step = max(1, int(fps * sample_interval_sec))
    
    best_similarity = 0.0
    best_timestamp = 0.0
    
    frame_idx = 0
    while True:
        # cap.grab() advances the stream at high speed without full YUV->RGB decompression
        grabbed = cap.grab()
        if not grabbed:
            break
            
        if frame_idx % frame_step == 0:
            ret, frame = cap.retrieve()
            if not ret or frame is None:
                break
                
            current_time = frame_idx / fps
            sim = calculate_frame_similarity(ref_img, frame)
            
            if sim > best_similarity:
                best_similarity = sim
                best_timestamp = current_time
                
            # Instant exit on high-confidence match
            if best_similarity >= 0.92:
                break
                
        frame_idx += 1
        
    cap.release()
    
    # Check if peak similarity meets our confidence threshold
    if best_similarity >= similarity_threshold:
        start_time = round(best_timestamp, 2)
        end_time = round(min(video_duration, start_time + scene_duration), 2)
        return (start_time, end_time, round(best_similarity, 3))
        
    return None
