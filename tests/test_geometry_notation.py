# -*- coding: utf-8 -*-
"""Mũi tên vectơ và ký hiệu góc phủ hết tên (owner, lỗi tái phát 18/11/2026).

Gốc lỗi: bản vá \\vec{AB} → \\overrightarrow{AB} nằm trong _legacy_sanitize_katex_latex, nhưng
preserve_math_and_code khóa nguyên mọi $...$ nên bản vá không bao giờ chạm tới công thức.
"""
import unittest

from services.markdown_tidy import (geometry_notation, geometry_notation_in_text,
                                    geometry_notation_inplace, wrap_vietnamese_in_math)
from services.text_boundaries import chemical_display_markdown, preserve_math_and_code


class GeometryNotation(unittest.TestCase):
    def test_two_point_vector_gets_long_arrow(self):
        self.assertEqual(geometry_notation(r"\vec{AB}"), r"\overrightarrow{AB}")
        self.assertEqual(geometry_notation(r"\vec{AA'}"), r"\overrightarrow{AA'}")
        self.assertEqual(geometry_notation(r"\vec {MN}"), r"\overrightarrow{MN}")
        self.assertEqual(geometry_notation(r"\vec AB"), r"\overrightarrow{AB}")

    def test_single_letter_vector_unchanged(self):
        for tex in (r"\vec{u}", r"\vec{a}+\vec{b}", r"\vec{i}", r"\vec{n_1}"):
            self.assertEqual(geometry_notation(tex), tex)

    def test_angle_gets_wide_symbol(self):
        self.assertEqual(geometry_notation(r"\hat{xOy}"), r"\widehat{xOy}")
        self.assertEqual(geometry_notation(r"\hat{ABC}=60^\circ"), r"\widehat{ABC}=60^\circ")
        self.assertEqual(geometry_notation(r"\hat{y}"), r"\hat{y}")  # ước lượng/ một chữ: giữ

    def test_only_inside_math_and_not_code(self):
        text = r"Cho $\vec{AB}=(1;2;3)$ và `\vec{AB}` trong mã."
        out = geometry_notation_in_text(text)
        self.assertIn(r"$\overrightarrow{AB}=(1;2;3)$", out)
        self.assertIn(r"`\vec{AB}`", out)

    def test_preserved_math_is_normalized(self):
        out = preserve_math_and_code(r"Góc $\hat{xOy}$ và $\vec{AB}$", lambda s: s)
        self.assertIn(r"$\widehat{xOy}$", out)
        self.assertIn(r"$\overrightarrow{AB}$", out)

    def test_display_paths(self):
        self.assertIn(r"\overrightarrow{AB}", chemical_display_markdown(r"B. $\vec{AB}=(2;-2;6)$", separate_steps=False))
        self.assertIn(r"\widehat{BAC}", wrap_vietnamese_in_math(r"Tính $\hat{BAC}$ (độ)"))

    def test_exam_inplace_keeps_object(self):
        exam = {"p1": [{"q": r"Tọa độ $\vec{AB}$ là", "opt": [r"A. $\vec{u}$"], "ans": "A"}]}
        same = geometry_notation_inplace(exam)
        self.assertIs(same, exam)
        self.assertEqual(exam["p1"][0]["q"], r"Tọa độ $\overrightarrow{AB}$ là")
        self.assertEqual(exam["p1"][0]["opt"], [r"A. $\vec{u}$"])
        self.assertEqual(exam["p1"][0]["ans"], "A")


if __name__ == "__main__":
    unittest.main()
