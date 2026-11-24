"""Generates search queries for scenes based on transcribed speech and context."""

import re
from typing import List, Tuple
from shorts_studio.analyzer.models import SceneCut, WordTimestamp

# Common English filler words that add little search value
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "which", "this", "that", "these", "those", "then", "just", "so", "than",
    "such", "both", "through", "about", "for", "is", "of", "while", "during",
    "to", "from", "in", "out", "on", "off", "again", "further", "then", "once"
}


def get_scene_spoken_words(scene: SceneCut, words: List[WordTimestamp]) -> List[WordTimestamp]:
    """Finds all words that fall within the time bounds of a given scene."""
    scene_words = []
    for w in words:
        # Check if the word overlaps with the scene time window (with a slight 0.15s tolerance)
        if (w.start_time >= (scene.start_time - 0.15)) and (w.end_time <= (scene.end_time + 0.15)):
            scene_words.append(w)
    return scene_words


def generate_scene_query(scene: SceneCut, words: List[WordTimestamp], fallback_topic: str = "viral short") -> Tuple[str, str]:
    """
    Extracts spoken text for a scene and produces an effective search query.
    Returns: (spoken_text, search_query)
    """
    scene_words = get_scene_spoken_words(scene, words)
    raw_text = " ".join(w.word for w in scene_words).strip()
    
    if not raw_text:
        # No speech in this scene: use fallback or topic query
        query = f"{fallback_topic} #shorts"
        return "", query

    # Clean punctuation: remove commas, dots, exclamation marks
    cleaned_words = [re.sub(r"[^\w\s]", "", w.word).strip() for w in scene_words]
    cleaned_words = [w for w in cleaned_words if w]
    
    # Filter out stopwords for the query while keeping key descriptive words
    meaningful_words = [w for w in cleaned_words if w.lower() not in STOP_WORDS]
    
    if len(meaningful_words) >= 2:
        query_terms = meaningful_words[:5]  # Limit to 5 strong keywords
    else:
        query_terms = cleaned_words[:5]
        
    query_str = " ".join(query_terms) + " #shorts"
    return raw_text, query_str
