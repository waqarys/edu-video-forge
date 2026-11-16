"""Render different scene types to video clips."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import subprocess
import tempfile


def render_scene(scene: Dict[str, Any], output: Path, theme: str = "chalkboard", quality: str = "medium", work_dir: Path = None):
    scene_type = scene.get("type", "chalkboard")
    if scene_type == "chalkboard":
        _render_chalkboard(scene, output, theme, quality)
    elif scene_type == "whiteboard":
        _render_whiteboard(scene, output, theme, quality)
    elif scene_type == "code":
        _render_code(scene, output, theme, quality)
    elif scene_type == "slides":
        _render_slides(scene, output, theme, quality)
    elif scene_type == "diagram" or scene_type == "architecture":
        _render_diagram(scene, output, theme, quality)
    elif scene_type == "terminal":
        _render_terminal(scene, output, theme, quality)
    elif scene_type == "diff":
        _render_diff(scene, output, theme, quality)
    elif scene_type == "webgl":
        _render_webgl(scene, output, work_dir)
    elif scene_type == "manim":
        _render_manim(scene, output, quality)
    else:
        _render_slides(scene, output, theme, quality)  # professional fallback


def _render_chalkboard(scene: Dict, output: Path, theme: str, quality: str):
    """Chalkboard-style Write animation (best for students)."""
    bg = "#1a1a1a" if theme == "chalkboard" else "#ffffff"
    text_color = "WHITE" if theme == "chalkboard" else "BLACK"
    content = scene.get("content", "Hello World").replace("\\", "\\\\")[:200]

    manim_code = f'''
from manim import *

class ChalkboardScene(Scene):
    def construct(self):
        self.camera.background_color = "{bg}"
        text = MathTex(r"{content}") if "\\" in r"{content}" else Text("{content}", color={text_color}, font_size=32)
        text.scale(0.7)
        self.play(Write(text), run_time=3)
        self.wait(1)
'''
    _run_manim(manim_code, output, quality)


def _render_whiteboard(scene: Dict, output: Path, theme: str, quality: str):
    """Clean professional whiteboard style for experienced developers."""
    content = scene.get("content", "Concept")[:150]
    manim_code = f'''
from manim import *

class WhiteboardScene(Scene):
    def construct(self):
        self.camera.background_color = "#f8f9fa"
        title = Text("Whiteboard", font_size=28, color=DARK_BLUE).to_edge(UP)
        text = Text("{content}", font_size=36, color=BLACK)
        self.play(FadeIn(title))
        self.play(Write(text))
        self.wait(1.5)
'''
    _run_manim(manim_code, output, quality)


def _render_slides(scene: Dict, output: Path, theme: str, quality: str):
    """Professional slide-style scene (title + bullets / content)."""
    content = scene.get("content", "Key Point").replace("\n", "\\n")
    manim_code = f'''
from manim import *

class SlideScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d1117"  # GitHub dark
        title = Text("Professional Slide", font_size=40, color=WHITE).to_edge(UP)
        body = Text("{content}", font_size=28, color=GREY_A, line_spacing=1.2)
        body.next_to(title, DOWN, buff=0.8)
        self.play(FadeIn(title))
        self.play(Write(body))
        self.wait(2)
'''
    _run_manim(manim_code, output, quality)


def _render_diagram(scene: Dict, output: Path, theme: str, quality: str):
    """Architecture / system diagram with boxes and arrows."""
    manim_code = '''
from manim import *

class DiagramScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d1117"
        client = Rectangle(width=2.5, height=1.2, color=BLUE).shift(LEFT*3)
        api = Rectangle(width=2.5, height=1.2, color=GREEN).shift(ORIGIN)
        db = Rectangle(width=2.5, height=1.2, color=ORANGE).shift(RIGHT*3)
        t1 = Text("Client", font_size=24).move_to(client)
        t2 = Text("API Gateway", font_size=24).move_to(api)
        t3 = Text("Database", font_size=24).move_to(db)
        arrow1 = Arrow(client.get_right(), api.get_left(), buff=0.1)
        arrow2 = Arrow(api.get_right(), db.get_left(), buff=0.1)
        self.play(Create(client), Write(t1))
        self.play(Create(arrow1))
        self.play(Create(api), Write(t2))
        self.play(Create(arrow2))
        self.play(Create(db), Write(t3))
        self.wait(1.5)
'''
    _run_manim(manim_code, output, quality)


def _render_terminal(scene: Dict, output: Path, theme: str, quality: str):
    """Animated terminal / CLI session."""
    content = scene.get("content", "$ git status\nOn branch main").replace("\n", "\\n")
    manim_code = f'''
from manim import *

class TerminalScene(Scene):
    def construct(self):
        self.camera.background_color = "#1e1e1e"
        terminal = Rectangle(width=10, height=5, color=GREY, fill_opacity=0.9)
        prompt = Text("{content}", font="Monospace", font_size=22, color=GREEN).scale(0.8)
        prompt.move_to(terminal)
        self.play(Create(terminal))
        self.play(AddTextLetterByLetter(prompt), run_time=3)
        self.wait(1)
'''
    _run_manim(manim_code, output, quality)


def _render_diff(scene: Dict, output: Path, theme: str, quality: str):
    """Before/After code comparison (side-by-side)."""
    manim_code = '''
from manim import *

class DiffScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d1117"
        before = Code(code="def old():\n    return 1", language="python", font_size=20).shift(LEFT*2.5)
        after = Code(code="def new():\n    return 2", language="python", font_size=20).shift(RIGHT*2.5)
        label1 = Text("Before", color=RED).next_to(before, UP)
        label2 = Text("After", color=GREEN).next_to(after, UP)
        self.play(FadeIn(label1), Create(before))
        self.play(FadeIn(label2), Create(after))
        self.wait(2)
'''
    _run_manim(manim_code, output, quality)


def _render_code(scene: Dict, output: Path, theme: str, quality: str):
    code = scene.get("content", "print('hello')")
    manim_code = f'''
from manim import *

class CodeScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d1117"
        code = Code(
            code="""{code}""",
            language="python",
            font="Monospace",
            font_size=22,
            background="window",
        )
        self.play(Create(code), run_time=2)
        self.wait(1.5)
'''
    _run_manim(manim_code, output, quality)


def _render_webgl(scene: Dict, output: Path, work_dir: Path):
    """Generate Three.js HTML for interactive-style concept explanations."""
    html = '''<!DOCTYPE html>
<html>
<head><title>WebGL Concept</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body style="margin:0;background:#111">
<script>
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
camera.position.z = 5;
function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
</script>
</body>
</html>'''
    html_path = (work_dir or Path(".")) / "webgl_scene.html"
    html_path.write_text(html)
    # Placeholder - full version uses Playwright for recording
    print(f"WebGL HTML generated at {html_path}")


def _render_manim(scene: Dict, output: Path, quality: str):
    code = scene.get("content", "")
    if "class" not in code:
        code = f"from manim import *\n\nclass CustomScene(Scene):\n    def construct(self):\n        {code}"
    _run_manim(code, output, quality)


def _run_manim(code: str, output: Path, quality: str):
    with tempfile.TemporaryDirectory() as tmp:
        py_file = Path(tmp) / "scene.py"
        py_file.write_text(code)
        qflag = {"low": "-ql", "medium": "-qm", "high": "-qh"}.get(quality, "-qm")
        try:
            subprocess.run(
                ["manim", qflag, "--disable_caching", str(py_file), "-o", str(output.stem)],
                cwd=tmp, check=True, capture_output=True
            )
            media = list(Path(tmp).rglob("*.mp4"))
            if media:
                media[0].replace(output)
        except Exception as e:
            print(f"Manim render failed: {e}")
            # Create empty placeholder so pipeline continues
            output.touch()
