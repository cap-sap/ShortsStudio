"""Speech transcription with word-level timestamps using faster-whisper."""

from typing import List
from faster_whisper import WhisperModel

from shorts_studio.analyzer.models import WordTimestamp


def transcribe_audio(
    audio_wav_path: str,
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8"
) -> List[WordTimestamp]:
    """
    Transcribes audio WAV file and extracts individual words with exact millisecond timestamps.
    Uses CTranslate2 CPU-quantized faster-whisper.
    """
    print(f"[*] Loading faster-whisper model ('{model_size}' on {device} with {compute_type})...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    print(f"[*] Transcribing audio: {audio_wav_path}")
    segments, info = model.transcribe(
        str(audio_wav_path),
        word_timestamps=True,
        vad_filter=True  # Voice Activity Detection to skip dead silence
    )
    
    words: List[WordTimestamp] = []
    
    for segment in segments:
        if segment.words:
            for w in segment.words:
                cleaned_word = w.word.strip()
                if cleaned_word:
                    words.append(WordTimestamp(
                        word=cleaned_word,
                        start_time=round(w.start, 3),
                        end_time=round(w.end, 3),
                        probability=round(w.probability, 3)
                    ))
                    
    print(f"[✓] Transcribed {len(words)} spoken words.")
    return words
