"""Unit tests for edu_video_forge.latex (no manim / LaTeX needed).  Run: python -m unittest discover tests"""
import unittest

from edu_video_forge.latex import classify_line, has_math, split_math, strip_math_delimiters, to_tex

QUAD = r"$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$"


class LatexHelpers(unittest.TestCase):
    def test_display_math_is_stripped(self):
        self.assertEqual(split_math(QUAD), [("math", r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}")])
        self.assertEqual(classify_line(QUAD), ("math", r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"))

    def test_inline_math(self):
        segs = split_math(r"Roots are $x_1$ and $x_2$.")
        self.assertEqual(segs, [("text", "Roots are "), ("math", "x_1"), ("text", " and "),
                                ("math", "x_2"), ("text", ".")])
        kind, tex = classify_line(r"Roots are $x_1$ and $x_2$.")
        self.assertEqual(kind, "mixed")
        self.assertEqual(tex, r"Roots are $x_1$ and $x_2$.")

    def test_bracket_delimiters(self):
        self.assertEqual(classify_line(r"\[ a^2 + b^2 = c^2 \]"), ("math", "a^2 + b^2 = c^2"))
        self.assertEqual(split_math(r"so \(y=mx\) holds")[1], ("math", "y=mx"))

    def test_plain_text(self):
        self.assertFalse(has_math("The quadratic formula:"))
        self.assertEqual(classify_line("- d > 0 : two real roots"), ("text", "- d > 0 : two real roots"))

    def test_escaped_dollar_is_text(self):
        self.assertFalse(has_math(r"costs \$5 today"))
        self.assertEqual(classify_line(r"costs \$5 today"), ("text", "costs $5 today"))

    def test_legacy_backslash_without_dollars(self):
        self.assertEqual(classify_line(r"\frac{1}{2}"), ("math", r"\frac{1}{2}"))

    def test_text_is_escaped_in_tex(self):
        self.assertEqual(to_tex([("text", "50% & #1 "), ("math", "a_b")]), r"50\% \& \#1 $a_b$")

    def test_strip_delimiters(self):
        self.assertEqual(strip_math_delimiters(r"Area $A = \pi r^2$"), r"Area A = \pi r^2")


if __name__ == "__main__":
    unittest.main()
