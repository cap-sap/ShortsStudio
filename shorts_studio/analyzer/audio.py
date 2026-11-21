"""Audio rhythm and energy spike detection using SciPy and NumPy."""

import numpy as np
from scipy.io import wavfile
from typing import List

from shorts_studio.analyzer.models import AudioCue


def analyze_audio_energy(
    audio_wav_path: str,
    window_ms: int = 50,
    peak_threshold_factor: float = 1.8
) -> List[AudioCue]:
    """
    Computes RMS audio energy over sliding windows to detect dynamic volume spikes
    and rhythmic onsets without needing heavy audio libraries.
    """
    print(f"[*] Analyzing audio energy dynamics on: {audio_wav_path}")
    sample_rate, samples = wavfile.read(str(audio_wav_path))
    
    # Convert integer PCM samples to normalized float (-1.0 to 1.0)
    if samples.dtype == np.int16:
        audio = samples.astype(np.float32) / 32768.0
    elif samples.dtype == np.int32:
        audio = samples.astype(np.float32) / 2147483648.0
    else:
        audio = samples.astype(np.float32)
        
    # Window parameters
    window_size = int(sample_rate * (window_ms / 1000.0))
    if window_size <= 0:
        return []
        
    num_windows = len(audio) // window_size
    if num_windows == 0:
        return []
        
    # Calculate Root Mean Square (RMS) energy per window
    trimmed = audio[:num_windows * window_size].reshape(num_windows, window_size)
    rms_energy = np.sqrt(np.mean(trimmed ** 2, axis=1))
    
    mean_energy = np.mean(rms_energy)
    if mean_energy < 1e-6:
        return []
        
    cues: List[AudioCue] = []
    
    # Peak detector: points where energy exceeds factor * mean_energy and is a local maximum
    for i in range(1, num_windows - 1):
        if rms_energy[i] > (peak_threshold_factor * mean_energy):
            if rms_energy[i] > rms_energy[i - 1] and rms_energy[i] > rms_energy[i + 1]:
                timestamp = round(i * (window_ms / 1000.0), 3)
                intensity = min(float(rms_energy[i] / (peak_threshold_factor * mean_energy)), 1.0)
                
                # Deduplicate peaks closer than 200ms
                if not cues or (timestamp - cues[-1].timestamp) >= 0.2:
                    cues.append(AudioCue(
                        timestamp=timestamp,
                        cue_type="energy_spike",
                        intensity=round(intensity, 2)
                    ))
                    
    print(f"[✓] Detected {len(cues)} audio energy peaks/cues.")
    return cues
