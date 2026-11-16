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
    elif scene_type == "code":
        _render_code(scene, output, theme, quality)
    elif scene_type == "webgl":
        _render_webgl(scene, output, work_dir)
    elif scene_type == "manim":
        _render_manim(scene, output, quality)
    else:
        _render_chalkboard(scene, output, theme, quality)  # fallback


def _render_chalkboard(scene: Dict, output: Path, theme: str, quality: str):
    """Chalkboard-style Write animation using Manim."""
    bg = "#1a1a1a" if theme == "chalkboard" else "#ffffff"
    text_color = "WHITE" if theme == "chalkboard" else "BLACK"
    content = scene.get("content", "Hello World").replace("\\", "\\\\")

    manim_code = f'''
from manim import *

class ChalkboardScene(Scene):
    def construct(self):
        self.camera.background_color = "{bg}"
        text = MathTex(r"{content}") if "\\" in r"{content}" else Text("{content[:100]}", color={text_color}, font_size=36)
        text.scale(0.8)
        self.play(Write(text), run_time=3)
        self.wait(1)
'''
    _run_manim(manim_code, output, quality)


def _render_code(scene: Dict, output: Path, theme: str, quality: str):
    code = scene.get("content", "print('hello')")
    manim_code = f'''
from manim import *

class CodeScene(Scene):
    def construct(self):
        code = Code(
            code="""{code}""",
            language="python",
            font="Monospace",
            font_size=24,
            background="window",
        )
        self.play(Create(code), run_time=2)
        self.wait(1)
'''
    _run_manim(manim_code, output, quality)


def _render_webgl(scene: Dict, output: Path, work_dir: Path):
    """Generate Three.js HTML. For full video, user can record or we use playwright later."""
    html = f'''<!DOCTYPE html>
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
const material = new THREE.MeshBasicMaterial({{color: 0x00ff00}});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
camera.position.z = 5;
function animate() {{
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>'''
    html_path = (work_dir or Path(".")) / "webgl_scene.html"
    html_path.write_text(html)
    # For now, create a placeholder video or note
    # In full version: use playwright to record canvas
    output.write_text("WebGL HTML generated at " + str(html_path))
    # Fallback: generate a simple static frame later


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
            # Move the rendered file
            media = list(Path(tmp).rglob("*.mp4"))
            if media:
                media[0].replace(output)
        except Exception as e:
            # Fallback simple video
            output.write_bytes(b"")  # placeholder
            print(f"Manim render failed: {e}")
