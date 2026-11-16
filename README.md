# EduVideoForge

**Complete, cross-platform pipeline to generate professional educational videos from scripts.**

Supports:
- Audio from script (TTS with precise timestamps)
- Chalkboard writing effects
- Generating code videos (typing, highlighting, progressive reveal)
- Explaining concepts using WebGL / Three.js
- Mathematical animations, effects, and diagrams (powered by Manim)
- Courses for school students (high-school math, science) and advanced professionals (e.g. Transformer architecture series)

**Platforms**: Works on Windows laptop and Mac Studio (and Linux). Python + Manim Community + FFmpeg + edge-tts.

**Integrations**:
- CLI designed for easy triggering by Grok Bot, Claude, OpenClaw, or any agent
- Standard MP4 output (with optional chapters and SRT) ready for OBS Studio, CapCut, or Final Cut Pro

## Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg in PATH (`brew install ffmpeg` / `choco install ffmpeg` / `apt install ffmpeg`)
- For best math rendering: LaTeX (MiKTeX on Windows, MacTeX on macOS)

```bash
git clone https://github.com/waqarys/edu-video-forge.git
cd edu-video-forge
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Generate your first video

```bash
python -m edu_video_forge generate examples/quadratic_formula.md --output quadratic.mp4 --voice en-US-AriaNeural --theme chalkboard
```

## Script Format

Markdown with clear scene markers (also supports JSON):

```markdown
# Quadratic Formula

## Scene: chalkboard
**Narration:** The quadratic formula solves equations of the form a x squared plus b x plus c equals zero.
**Content:**
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}

## Scene: code
**Narration:** Here is a simple Python function.
**Content:**
```python
def quadratic(a, b, c):
    d = b**2 - 4*a*c
    return (-b + d**0.5) / (2*a)
```
```

## Architecture

1. Parse script into ordered scenes
2. Generate TTS audio + word/sentence timestamps per scene (edge-tts)
3. Render visual clips:
   - `chalkboard` → dark background + Manim `Write` animation
   - `code` → Manim `Code` with line-by-line or character reveal
   - `webgl` → Generate self-contained Three.js HTML (record via browser or headless)
   - `manim` → Full custom Manim scene
4. Compose final video with FFmpeg (exact sync to narration durations, crossfades)
5. Export MP4 + SRT subtitles + chapters metadata

## Using with Agents (OpenClaw / Grok / Claude)

Agents can simply execute the CLI:

```bash
python -m edu_video_forge generate --script course/lesson01.md --output out/lesson01.mp4 --quality high
```

Or use the Python API:

```python
from edu_video_forge import generate_video
generate_video("script.md", "output.mp4", theme="chalkboard")
```

## Project Structure

- `edu_video_forge/` – core package
- `examples/` – ready-to-run scripts (high-school math + Transformer attention)
- `requirements.txt`
- Full pipeline is modular and testable

## License
MIT

Built to help educators and course creators produce high-quality animated videos entirely from a laptop.
