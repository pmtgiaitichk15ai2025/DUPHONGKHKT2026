# -*- coding: utf-8 -*-
"""Stems must not leak f={...} plot JSON; graphs still coerce from string f."""
from __future__ import annotations

import unittest

from services.exam_visual_sanitize import (
    coerce_plot_spec,
    sanitize_exam_visuals,
    sanitize_question_visuals,
    strip_inline_plot_specs,
)


class StripInlinePlotSpecsTests(unittest.TestCase):
    def test_strips_f_equals_json_and_promotes(self):
        stem = (
            'Cho đồ thị như hình bên f={"type":"func_3","a":1,"b":-3,"c":0,"d":2}. '
            "Hàm số đạt cực tiểu tại điểm nào?"
        )
        cleaned, specs = strip_inline_plot_specs(stem)
        self.assertNotIn("func_3", cleaned)
        self.assertNotIn("f=", cleaned)
        self.assertIn("hình bên", cleaned)
        self.assertIn("cực tiểu", cleaned)
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0]["spec"]["type"], "func_3")
        self.assertEqual(specs[0]["spec"]["a"], 1)

    def test_strips_bare_type_object(self):
        stem = 'Đồ thị {"type":"func_1_1","a":1,"b":1,"c":1,"d":-1} của hàm số nào dưới đây?'
        cleaned, specs = strip_inline_plot_specs(stem)
        self.assertNotIn('"type"', cleaned)
        self.assertEqual(specs[0]["spec"]["type"], "func_1_1")


class SanitizeQuestionTests(unittest.TestCase):
    def test_promotes_leaked_f_and_cleans_stem(self):
        q = {
            "q": 'Cho đồ thị f={"type":"func_3","a":1,"b":0,"c":-3,"d":1}. Tìm số điểm cực trị.',
            "opt": ["A. 0", "B. 1", "C. 2", "D. 3"],
            "ans": "C",
        }
        out = sanitize_question_visuals(q)
        self.assertNotIn("func_3", out["q"])
        self.assertEqual(out["f"]["type"], "func_3")
        self.assertEqual(out["f"]["d"], 1)

    def test_coerces_string_f_field(self):
        q = {
            "q": "Cho đồ thị như hình bên. Hàm số nghịch biến trên khoảng nào?",
            "f": '{"type":"func_3","a":1,"b":-3,"c":0,"d":2}',
        }
        out = sanitize_question_visuals(q)
        self.assertIsInstance(out["f"], dict)
        self.assertEqual(out["f"]["type"], "func_3")
        self.assertIs(coerce_plot_spec(out["f"]), out["f"])

    def test_drops_json_dumped_bbt_object(self):
        q = {"q": "Cho BBT như hình.", "bbt": {"type": "func_3", "a": 1}}
        out = sanitize_question_visuals(q)
        self.assertNotIn("bbt", out)

    def test_exam_walk(self):
        exam = {
            "p1": [
                {
                    "q": 'f={"type":"parabola","a":1,"b":0,"c":0} đồ thị nào?',
                    "opt": ["A", "B", "C", "D"],
                    "ans": "A",
                }
            ],
            "p2": [],
            "p3": [],
        }
        out = sanitize_exam_visuals(exam)
        self.assertNotIn("parabola", out["p1"][0]["q"])
        self.assertEqual(out["p1"][0]["f"]["type"], "parabola")


class AppWiringTests(unittest.TestCase):
    def test_app_and_delivery_call_sanitize(self):
        from pathlib import Path

        app = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        policy = (
            Path(__file__)
            .resolve()
            .parents[1]
            .joinpath("services/curriculum_policy.py")
            .read_text(encoding="utf-8")
        )
        self.assertIn("strip_inline_plot_specs", app)
        self.assertIn("sanitize_question_visuals", app)
        self.assertIn("coerce_plot_spec", app)
        self.assertIn("sanitize_exam_visuals", policy)
        contract = (
            Path(__file__)
            .resolve()
            .parents[1]
            .joinpath("services/web_question_contract.py")
            .read_text(encoding="utf-8")
        )
        self.assertIn("trường JSON riêng", contract)
        self.assertIn("không chèn chữ `f={...}`", contract)


if __name__ == "__main__":
    unittest.main()
