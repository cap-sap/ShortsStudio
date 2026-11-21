# ShortsStudio - Project Context & Living Documentation

## 1. Project Overview & Goal
**ShortsStudio** is a local, AI-powered system designed to analyze viral short-form videos (YouTube Shorts, Instagram Reels, TikTok) and assist in recreating their editing style.

The end goal is a modular pipeline that:
1. **Analyzes Reference Videos**: Deconstructs cuts, scene pacing, zooms, pan/motion, transitions, speech/captions, and background audio.
2. **Discovers Source Footage**: Identifies matching or original high-resolution clips based on reference scene semantics.
3. **Enables Human Curation**: A visual interface to inspect, swap, trim, and approve clips.
4. **Generates Edit Timelines**: Produces a standardized, declarative timeline specification (JSON).
5. **Automates Assembly**: Renders cuts, animated kinetic typography, sound effects, music sync, zooms, and transitions.
6. **Provides Visual Adjustment**: Enables fine-tuning of timings, captions, and effects before final render.
7. **Exports Final Video**: Delivers high-quality 9:16 vertical video optimized for social platforms.

---

## 2. Technical Environment & Hardware Constraints
- **Operating System**: Windows 11
- **Machine**: Lenovo ThinkPad T495
- **Processor**: AMD Ryzen 7 3700U (4 Cores / 8 Threads, 2.3 GHz base, up to 4.0 GHz boost)
- **Memory**: 16 GB RAM
- **Graphics**: Integrated AMD Radeon RX Vega 10 (No dedicated NVIDIA GPU / No CUDA)

### Optimization Guidelines for this Machine:
- **CPU-Friendly AI Models**: Avoid heavy PyTorch/CUDA-dependent architectures. Use quantized models (e.g., `CTranslate2` / `int8` in `faster-whisper`). For speech recognition, target `base` or `small` models.
- **Proxy-Based Analysis**: Run computer vision and scene detection on low-resolution downscaled proxies (e.g., 360p) rather than full 1080x1920 frames to conserve CPU and RAM.
- **Efficient Video Encoding**: Utilize `ffmpeg` with fast CPU presets (`-preset veryfast`) or leverage AMD AMF hardware encoding if compatible.
- **Memory Management**: Process video analysis in streams or batches to avoid holding uncompressed frames in memory.

---

## 3. Technology Stack
| Layer | Planned Technology | Role |
| :--- | :--- | :--- |
| **Orchestration & Backend** | Python (3.10 - 3.12 recommended) | Core logic, pipelines, API integrations |
| **User Interface** | Streamlit | Initial interactive dashboard & approval UI |
| **Media Engine** | FFmpeg & FFprobe (v8.1.1 installed) | Audio/video extraction, transcoding, fast cut assembly |
| **Video Analysis** | OpenCV (`opencv-python-headless`), PySceneDetect | Scene boundary detection, motion analysis, frame difference |
| **Audio & Speech** | `faster-whisper`, Librosa / Aubio | Transcription, word-level timestamps, beat/music detection |
| **Advanced Video Editing** | Remotion (Node.js/React) | Kinetic animated captions, overlays, dynamic transitions |
| **Timeline Schema** | JSON | Declarative timeline exchange format between analyzer & renderer |
| **Version Control** | Git | Project history and branch management |

---

## 4. Current Environment Status & Audit
- [x] **Workspace**: `D:\ShortsStudio` initialized.
- [x] **FFmpeg & Media Tools**: Present in `D:\yt-dpl` (`ffmpeg.exe` v8.1.1, `ffprobe.exe`, `yt-dlp.exe`). FFmpeg is globally accessible in PATH.
- [x] **Node.js**: Present at `C:\Program Files\nodejs\node.exe`.
- [x] **Python Runtime**: Python 3.11.9 installed at `D:\applicatons\Python311\python.exe`.
- [x] **Virtual Environment**: Dedicated `.venv` created at `D:\ShortsStudio\.venv` using Python 3.11.9.
- [x] **Git & GitHub Setup**: Git repository initialized with `.gitignore`. Configured user: `cap-sap` (`saifurrehman18158@gmail.com`). Remote repository connected to `https://github.com/cap-sap/ShortsStudio.git` and pushed to `main`.

---

## 5. Development Roadmap
- **Phase 1: Reference Video Analyzer** - [x] **COMPLETED**
  - [x] Dependencies installed (`scenedetect`, `faster-whisper`, `numpy`, `scipy`, `pydantic`).
  - [x] Ingestion module (`shorts_studio/analyzer/ingest.py`): URL download via `yt-dlp` or local video ingestion + 360p CPU proxy generation + 16kHz mono WAV extraction.
  - [x] Scene/Cut detection module (`shorts_studio/analyzer/scenes.py`): ContentDetector based scene boundary identification.
  - [x] Kinetic speech transcription (`shorts_studio/analyzer/transcribe.py`): faster-whisper (CTranslate2 `int8` CPU) with word-level millisecond timestamps.
  - [x] Audio analysis module (`shorts_studio/analyzer/audio.py`): RMS sliding-window energy dynamics and audio peak detection.
  - [x] Timeline specification & exporter (`shorts_studio/analyzer/models.py`, `pipeline.py`): Unified JSON schema output (`timeline.json`).
  - [x] Verified on real test clip (`D:\sources\ai tantrum.mp4`).
- **Phase 2: Source Footage Discovery** *(Next Target)*
  - Semantic query extraction per scene from transcribed speech and visual context
  - Automated footage search and retrieval (Pexels / Pixabay API, YouTube search, or local footage library)
  - Video downloading and clipping candidate matches
- **Phase 3: Human Approval of Footage**
- **Phase 4: Automated Editing Engine**
- **Phase 5: Advanced Editing Styles, Captions & Audio Matching**
- **Phase 6: Quality Checking & Export**
- **Phase 7: Full Workflow Automation**

---

## 6. Known Issues & Immediate Next Steps
1. **Phase 2 Planning**: Discuss source footage discovery strategy (e.g., local clip matching vs. free stock API integration like Pexels vs. YouTube search).
2. **Push Phase 1 to GitHub**: Ensure all working Phase 1 modules are committed and pushed to `https://github.com/cap-sap/ShortsStudio.git`.
