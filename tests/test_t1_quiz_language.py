# -*- coding: utf-8 -*-
"""Web 18/11/2026: Trạm 1 Toán 12 sinh Phần 2 bằng tiếng Anh dù bài học tiếng Việt."""
import unittest

from services.curriculum_policy import item_display_language_issue, lesson_prompt


class T1QuizLanguage(unittest.TestCase):
    def test_prompt_requires_vietnamese_quiz(self):
        self.assertIn("Phần 2, Phần 3 viết bằng tiếng Việt", lesson_prompt("Toán học", 12, "Biểu thức toạ độ"))

    def test_web_english_stem_is_flagged(self):
        stem = ("In the Oxyz space, given two vectors $\vec{a}=(1;-2;3)$ and $\vec{b}=(3;0;-1)$, "
                "what are the coordinates of the vector $\vec{a}+\vec{b}$?")
        self.assertTrue(item_display_language_issue(stem, "Toán học"))
        self.assertFalse(item_display_language_issue("Trong không gian Oxyz, cho hai vectơ $\vec a$.", "Toán học"))


if __name__ == "__main__":
    unittest.main()
