# EduVideoForge

**Complete, cross-platform pipeline to generate professional educational videos from scripts.**

Supports:
- Audio from script (TTS with precise timestamps)
- Chalkboard writing effects (ideal for students)
- Professional scenes for experienced engineers (5–20+ years)
- Generating code videos (typing, highlighting, progressive reveal)
- Explaining concepts using WebGL / Three.js
- Mathematical animations, effects, and diagrams (powered by Manim)
- Courses for school students and advanced professionals (system design, transformers, architecture, **design patterns**)

**Platforms**: Works on Windows laptop and Mac Studio (and Linux). Python + Manim Community + FFmpeg + edge-tts.

**Integrations**:
- CLI designed for easy triggering by Grok Bot, Claude, OpenClaw, or any agent
- Standard MP4 output (with optional chapters and SRT) ready for OBS Studio, CapCut, or Final Cut Pro
- Easy GIF export of short loops via FFmpeg post-processing

## Scene Types

### For Students
- `chalkboard` — Hand-writing style on dark board

### For Experienced Professionals (industry standard)
- `slides` — Clean dark-mode slides with title + bullets (GitHub-style)
- `diagram` / `architecture` — Boxes, arrows, system flows
- `sequence` — Animated sequence diagrams (actors + messages)
- `class-diagram` / `uml` — UML class diagrams with inheritance & composition (ideal for Design Patterns)
- `metrics` / `chart` — Animated bar charts / metrics growth
- `mermaid` — Mermaid syntax support (saves .mmd + animated fallback)
- `terminal` — Animated CLI / terminal sessions
- `diff` — Side-by-side before/after code comparison
- `whiteboard` — Clean professional whiteboard (lighter than chalkboard)
- `code` — Syntax-highlighted code with progressive reveal
- `webgl` — Three.js / WebGL interactive-style visualizations
- `manim` — Full custom Manim scenes

These match what senior engineers and tech companies use in internal talks, conference talks, architecture reviews, and advanced courses.

## Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg in PATH (`brew install ffmpeg` / `choco install ffmpeg` / `apt install ffmpeg`)
- For best math rendering: LaTeX (MiKTeX on Windows, MacTeX on macOS)
- Optional: mermaid-cli (`npm install -g @mermaid-js/mermaid-cli`) for full Mermaid rendering

```bash
git clone https://github.com/waqarys/edu-video-forge.git
cd edu-video-forge
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Generate videos

**High-school style:**
```bash
python -m edu_video_forge generate examples/quadratic_formula.md --output quadratic.mp4 --theme chalkboard
```

**Professional / system design:**
```bash
python -m edu_video_forge generate examples/professional_system_design.md --output system_design.mp4
```

**Design Patterns (Strategy):**
```bash
python -m edu_video_forge generate examples/design_patterns_strategy.md --output strategy.mp4
```

**Advanced (sequence + metrics + mermaid):**
```bash
python -m edu_video_forge generate examples/advanced_professional.md --output advanced.mp4
```

**Advanced AI series:**
```bash
python -m edu_video_forge generate examples/transformer_attention.md --output attention.mp4
```

### GIF export (short loops)
After generating an MP4, create a GIF with:
```bash
ffmpeg -i advanced.mp4 -vf "fps=10,scale=640:-1:flags=lanczos" -c:v gif advanced.gif
```

## Script Format

Markdown with clear scene markers (also supports JSON):

```markdown
## Scene: sequence
**Narration:** Request sequence through the system.
**Content:**
Client -> Gateway -> Service

## Scene: class-diagram
**Narration:** UML for the Strategy pattern.
**Content:**
Context uses Strategy interface

## Scene: metrics
**Narration:** Quarterly growth.
**Content:**
Q1 Q2 Q3 Q4
```

## Architecture

1. Parse script into ordered scenes
2. Generate TTS audio + word/sentence timestamps per scene (edge-tts)
3. Render visual clips according to scene type
4. Compose final video with FFmpeg (sync to narration)
5. Export MP4 + SRT subtitles + chapters metadata

## Using with Agents (OpenClaw / Grok / Claude)

```bash
python -m edu_video_forge generate --script course/lesson01.md --output out/lesson01.mp4 --quality high
```

Or Python API:

```python
from edu_video_forge import generate_video
generate_video("script.md", "output.mp4")
```

## Roadmap / Known Gaps (from open-source comparison)

High-priority items for production-quality course content:
- Optional `manim-voiceover` integration for tighter word-level animation sync + better TTS backends
- Content-driven (not hardcoded) sequence and class diagrams
- Optional background music track
- Simple retry/self-healing on Manim render failures
- Chapter markers in final MP4

## Project Structure

- `edu_video_forge/` – core package (parser, renderers, pipeline, CLI)
- `examples/` – ready-to-run scripts (students + professionals + design patterns)
- `requirements.txt` + `pyproject.toml`

## License
MIT

Built to help educators and course creators produce high-quality animated videos entirely from a laptop — from high-school math to senior engineering content (including Design Patterns).
