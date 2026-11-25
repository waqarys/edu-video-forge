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
- Optional background music and embedded chapter markers

**Platforms**: Works on Windows laptop and Mac Studio (and Linux). Python + Manim Community + FFmpeg + edge-tts.

**Integrations**:
- CLI designed for easy triggering by Grok Bot, Claude, OpenClaw, or any agent
- Standard MP4 output (with chapters and SRT) ready for OBS Studio, CapCut, or Final Cut Pro
- Easy GIF export of short loops via FFmpeg post-processing

## Scene Types

### For Students
- `chalkboard` — Hand-writing style on dark board

### For Experienced Professionals (industry standard)
- `slides` — Clean dark-mode slides with title + bullets (GitHub-style)
- `diagram` / `architecture` — Boxes, arrows, system flows (content-aware labels)
- `sequence` — Animated sequence diagrams (content-aware actors)
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
- For best math rendering: a LaTeX distribution (soft requirement, see [Math / LaTeX](#math--latex))
- Optional: mermaid-cli (`npm install -g @mermaid-js/mermaid-cli`) for full Mermaid rendering

```bash
git clone https://github.com/waqarys/edu-video-forge.git
cd edu-video-forge
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
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

**With background music and chapters (default):**
```bash
python -m edu_video_forge generate examples/design_patterns_strategy.md \
  --output strategy.mp4 \
  --bg-music /path/to/calm-music.mp3
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

## Math / LaTeX

Manim draws formulas with LaTeX, so a TeX distribution is a **soft requirement**: everything renders
without it, but math then falls back to plain text.

- **Windows:** [MiKTeX](https://miktex.org/) (enable "install missing packages on the fly")
- **macOS:** [MacTeX](https://tug.org/mactex/) (or BasicTeX + `sudo tlmgr install standalone preview doublestroke`)
- **Linux:** TeX Live, e.g. `sudo apt install texlive-latex-base texlive-latex-extra texlive-fonts-recommended dvisvgm`

`latex` and `dvisvgm` must be on PATH (check with `latex --version` and `dvisvgm --version`).

How chalkboard content is read (one board row per line):

| Content line | Rendered as |
|---|---|
| `$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$` or `\[ ... \]` | `MathTex` (dollar signs stripped) |
| `Roots are $x_1$ and $x_2$.` (inline `$...$` / `\( ... \)`) | `Tex`: text with inline math |
| `\frac{1}{2}` (backslash commands, no dollars; legacy) | `MathTex` |
| anything else | `Text` |

Write `\$` for a literal dollar sign. If LaTeX is missing or a formula fails to compile, that line is
drawn as plain text without the `$` delimiters and a warning is printed. Parsing lives in
`edu_video_forge/latex.py` (tests: `python -m unittest discover tests`).

## Architecture

1. Parse script into ordered scenes
2. Generate TTS audio + word/sentence timestamps per scene (edge-tts)
3. Render visual clips according to scene type (with retry on Manim failure)
4. Compose final video with FFmpeg (sync to narration)
5. Optionally mix low-volume background music
6. Embed chapter markers from scene narration
7. Export MP4 + SRT subtitles

## Using with Agents (OpenClaw / Grok / Claude)

```bash
python -m edu_video_forge generate --script course/lesson01.md --output out/lesson01.mp4 --quality high
```

Or Python API:

```python
from edu_video_forge import generate_video
generate_video("script.md", "output.mp4", bg_music="music.mp3")
```

## Optional: Higher-quality Voiceover

For tighter word-level animation sync and better voices, you can install the official Manim Voiceover plugin and use it in custom `manim` scenes:

```bash
pip install manim-voiceover[gtts]          # free gTTS
# or
pip install manim-voiceover[gemini]        # recommended (needs Google credentials)
```

See https://voiceover.manim.community for examples using `VoiceoverScene`.

## Roadmap / Remaining Gaps

- Deeper automatic integration of manim-voiceover into all scene types (currently best used for custom manim scenes)
- More advanced content-driven diagram parsing (PlantUML/Mermaid full render)
- Voice cloning options

## Project Structure

- `edu_video_forge/` – core package (parser, renderers, pipeline, CLI)
- `examples/` – ready-to-run scripts (students + professionals + design patterns)
- `requirements.txt` + `pyproject.toml`

## License
MIT

Built to help educators and course creators produce high-quality animated videos entirely from a laptop — from high-school math to senior engineering content (including Design Patterns).
