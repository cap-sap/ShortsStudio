"""Visual query generator combining keyframe visual cues and context."""

import cv2
import re
from pathlib import Path
from typing import List, Optional

from shorts_studio.discovery.models import KeyframeInfo
from shorts_studio.analyzer.models import WordTimestamp, SceneCut
from shorts_studio.discovery.query_gen import get_scene_spoken_words, STOP_WORDS


def analyze_keyframe_colors(image_path: str) -> dict:
    """Computes dominant color tones in HSV to recognize jerseys or scenery."""
    img = cv2.imread(str(image_path))
    if img is None:
        return {}
        
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_mean = hsv[:, :, 0].mean()
    s_mean = hsv[:, :, 1].mean()
    v_mean = hsv[:, :, 2].mean()
    
    return {
        "hue_mean": round(float(h_mean), 2),
        "saturation_mean": round(float(s_mean), 2),
        "value_mean": round(float(v_mean), 2),
    }


def extract_video_global_context(words: List[WordTimestamp]) -> List[str]:
    """Finds the most frequent capitalized named entities (people, teams) across the whole video."""
    all_names = []
    for w in words:
        clean = re.sub(r"[^\w\s]", "", w.word).strip()
        if clean and clean[0].isupper() and clean.lower() not in STOP_WORDS:
            all_names.append(clean)
            
    from collections import Counter
    counts = Counter(all_names)
    return [name for name, _ in counts.most_common(3)]


def generate_visual_search_query(
    scene: SceneCut,
    keyframes: List[KeyframeInfo],
    words: Optional[List[WordTimestamp]] = None,
    overall_topic: Optional[str] = None
) -> str:
    """
    Constructs an accurate search query to find the raw/original video of this scene.
    Combines:
    1. Global subject entities (e.g., Tatum, Brown, Luka, LeBron) so all scenes retain context.
    2. Scene-specific actions and words.
    3. Target keywords optimized for YouTube/Google raw footage discovery.
    """
    all_words = words or []
    global_entities = extract_video_global_context(all_words)
    
    # Extract entities and key nouns from scene words if available
    scene_words = get_scene_spoken_words(scene, all_words)
    clean_words = [re.sub(r"[^\w\s]", "", w.word).strip() for w in scene_words]
    clean_words = [w for w in clean_words if w]
    
    # Identify proper nouns / capitalized names or key words
    proper_names = [w for w in clean_words if w[0].isupper() and w.lower() not in STOP_WORDS]
    action_words = [w for w in clean_words if w.lower() not in STOP_WORDS and w not in proper_names]
    
    query_parts = []
    
    # 1. Anchor with the video's primary subject entities (e.g. Tatum, Brown)
    for ent in global_entities:
        if ent not in query_parts:
            query_parts.append(ent)
            
    # 2. Add scene-specific proper names and actions
    for p in proper_names:
        if p not in query_parts:
            query_parts.append(p)
            
    for a in action_words[:3]:
        if a not in query_parts:
            query_parts.append(a)
            
    if not query_parts:
        if overall_topic:
            query_parts.append(overall_topic)
        else:
            query_parts.append(f"scene {scene.scene_id} original clip")
            
    query_str = " ".join(query_parts) + " original clip"
    return query_str
