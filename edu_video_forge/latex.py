"""Helpers for LaTeX math in scene content.

Expected format (chalkboard / whiteboard ``**Content:**``):

* Display math on its own line:   ``$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$``  (``\\[ ... \\]`` also works)
* Inline math inside a sentence:  ``The roots are $x_1$ and $x_2$.``
* A line with backslash commands but no dollars (legacy format) is treated as one math line.
* Everything else is plain text.  Use ``\\$`` for a literal dollar sign.

Dollar delimiters are always stripped before the math reaches ``MathTex`` / ``Tex``.
If no LaTeX install is found the renderer falls back to plain ``Text`` (with the
delimiters removed) and logs a warning.
"""
from __future__ import annotations

import re
import shutil
from typing import List, Tuple

Segment = Tuple[str, str]  # (kind, value) where kind is "text" | "math"

# $$...$$, \[...\], $...$ (not escaped \$), \(...\)
_MATH_RE = re.compile(
    r"(?<!\\)\$\$(?P<dd>.+?)(?<!\\)\$\$"
    r"|\\\[(?P<br>.+?)\\\]"
    r"|(?<!\\)\$(?P<d>[^$]+?)(?<!\\)\$"
    r"|\\\((?P<pa>.+?)\\\)",
    re.DOTALL,
)
_TEX_SPECIALS = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_",
    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "$": r"\$",
}


def has_math(text: str) -> bool:
    """True if the text contains delimited math ($..$, $$..$$, \\[..\\], \\(..\\))."""
    return bool(_MATH_RE.search(text or ""))


def split_math(line: str) -> List[Segment]:
    """Split one line into text / math segments. Delimiters are removed from math segments.

    A line with LaTeX commands but no delimiters (legacy ``\\frac{a}{b}`` content) is one math segment.
    """
    line = line or ""
    segs: List[Segment] = []
    pos = 0
    for m in _MATH_RE.finditer(line):
        if m.start() > pos:
            segs.append(("text", line[pos:m.start()]))
        body = next(g for g in (m.group("dd"), m.group("br"), m.group("d"), m.group("pa")) if g is not None)
        segs.append(("math", body.strip()))
        pos = m.end()
    if pos < len(line):
        segs.append(("text", line[pos:]))
    if not any(k == "math" for k, _ in segs) and re.search(r"\\[A-Za-z]+", line):
        return [("math", line.strip())]
    segs = [(k, v) for k, v in segs if v.strip() or k == "math"]
    return [(k, v.replace("\\$", "$") if k == "text" else v) for k, v in segs]


def strip_math_delimiters(text: str) -> str:
    """Plain-text version of a line: math bodies kept, $ / \\[ \\] delimiters removed."""
    return "".join(v for _, v in split_math(text)).strip() if text else ""


def escape_tex(text: str) -> str:
    """Escape text-mode LaTeX special characters."""
    return "".join(_TEX_SPECIALS.get(c, c) for c in text)


def to_tex(segments: List[Segment]) -> str:
    """Build a ``Tex`` string: text escaped, math wrapped in ``$...$``."""
    out = []
    for kind, val in segments:
        out.append(f"${val}$" if kind == "math" else escape_tex(val))
    return "".join(out).strip()


def classify_line(line: str) -> Tuple[str, str]:
    """Return (kind, payload) for one content line.

    kind: "math"  -> payload is a MathTex string (whole line is a formula)
          "mixed" -> payload is a Tex string (text with inline $math$)
          "text"  -> payload is plain text
    """
    segs = split_math(line)
    kinds = {k for k, _ in segs}
    if kinds == {"math"} and len(segs) == 1:
        return "math", segs[0][1]
    if "math" in kinds:
        return "mixed", to_tex(segs)
    return "text", line.replace("\\$", "$")


def latex_available() -> bool:
    """Manim needs `latex` (or the configured tex compiler) plus `dvisvgm` on PATH."""
    return bool((shutil.which("latex") or shutil.which("pdflatex")) and shutil.which("dvisvgm"))
